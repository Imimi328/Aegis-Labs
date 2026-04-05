from fastapi import FastAPI, UploadFile, File, Form, Query
import sqlite3
import tempfile
import threading
import time
import yt_dlp
import numpy as np
import cv2
import torch
from transformers import AutoProcessor, AutoModel
from PIL import Image
import requests
import json
import uvicorn
from fastapi.middleware.cors import CORSMiddleware


# ----------------------------------------
# CONFIG
# ----------------------------------------
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# ---- Google SigLIP ----
print("Loading Google SigLIP model...")
processor = AutoProcessor.from_pretrained("google/siglip-base-patch16-224")
vision_model = AutoModel.from_pretrained("google/siglip-base-patch16-224").to(DEVICE)

# ---- Gemma (local API via llama.cpp / LM Studio) ----
LLM_API_URL = "http://localhost:1234/v1/chat/completions"
LLM_MODEL = "gemma-4e4b"

# ----------------------------------------
# FASTAPI INIT (DOCUMENTED)
# ----------------------------------------
app = FastAPI(
    title="Emogi Detection API",
    description="""
AI-powered video reupload detection system.

Features:
- Upload video
- Continuous YouTube scanning
- AI similarity detection

Stack:
- Google SigLIP (vision embeddings)
- Gemma LLM (query generation)
""",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https://.*\.emogi\.space|https://emogi\.space",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------
# DATABASE
# ----------------------------------------
def get_db():
    return sqlite3.connect("emogi.db", check_same_thread=False)

def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        status TEXT,
        video_path TEXT,
        title TEXT,
        description TEXT,
        language TEXT,
        country TEXT,
        latest_timestamp INTEGER DEFAULT 0
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id INTEGER,
        title TEXT,
        url TEXT,
        score REAL
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ----------------------------------------
# YT-DLP CONFIG
# ----------------------------------------
def ydl_opts():
    return {
        "quiet": True,
        "no_warnings": True,
        "format": "best[ext=mp4]/best",
        "ignoreerrors": True,
        "noplaylist": True,
        "extractor_args": {
            "youtube": {
                "player_client": ["android"]
            }
        }
    }

# ----------------------------------------
# SIGLIP FEATURE EXTRACTION
# ----------------------------------------
def extract_features(path):
    frames = []
    cap = cv2.VideoCapture(path)

    while len(frames) < 12:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.resize(frame, (224, 224))
        frames.append(frame)

    cap.release()

    if not frames:
        return None

    embs = []
    for f in frames:
        img = Image.fromarray(cv2.cvtColor(f, cv2.COLOR_BGR2RGB))

        inputs = processor(images=img, return_tensors="pt").to(DEVICE)

        with torch.no_grad():
            outputs = vision_model.get_image_features(**inputs)
            outputs = outputs / outputs.norm(dim=-1, keepdim=True)

        embs.append(outputs.cpu().numpy())

    return np.vstack(embs)

# ----------------------------------------
# SIMILARITY MATCHING
# ----------------------------------------
def match_video(src, tgt):
    sim = tgt @ src.T
    frame_scores = np.max(sim, axis=1)

    strong = frame_scores > 0.85
    ratio = np.sum(strong) / len(frame_scores)
    avg = np.mean(frame_scores)

    return ratio * avg, avg

# ----------------------------------------
# GEMMA QUERY GENERATION
# ----------------------------------------
def generate_queries(title, description, language, country):
    prompt = f"""
Generate YouTube search queries for detecting reuploads.

Title: {title}
Description: {description}
Language: {language}
Country: {country}

Include:
- highlights
- clips
- edits
- shorts
- reuploads

Return ONLY a JSON array.
"""

    try:
        res = requests.post(
            LLM_API_URL,
            headers={"Content-Type": "application/json"},
            json={
                "model": LLM_MODEL,
                "messages": [
                    {"role": "system", "content": "Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3
            },
            timeout=60
        )

        data = res.json()
        text = data["choices"][0]["message"]["content"].strip()

        if "```" in text:
            text = text.split("```")[1]

        return json.loads(text)

    except Exception as e:
        print("LLM error:", e)
        return [title]

# ----------------------------------------
# WORKER LOOP
# ----------------------------------------
def worker_loop():
    print("Worker started...")
    processed_ids = set()

    while True:
        conn = get_db()
        cur = conn.cursor()

        cur.execute("SELECT * FROM jobs WHERE status='running'")
        jobs = cur.fetchall()

        for job in jobs:
            job_id = job[0]
            video_path = job[2]
            title = job[3]
            description = job[4]
            language = job[5]
            country = job[6]
            latest_ts = job[7]

            source_emb = extract_features(video_path)
            if source_emb is None:
                continue

            queries = generate_queries(title, description, language, country)

            with yt_dlp.YoutubeDL(ydl_opts()) as ydl:
                for q in queries:
                    try:
                        data = ydl.extract_info(f"ytsearch10:{q}", download=False)
                    except:
                        continue

                    for e in data.get("entries", []):
                        if not e:
                            continue

                        vid = e.get("id")
                        if not vid or vid in processed_ids:
                            continue

                        ts = e.get("timestamp", 0)
                        if ts <= latest_ts:
                            continue

                        url = f"https://www.youtube.com/watch?v={vid}"

                        try:
                            info = ydl.extract_info(url, download=False)
                            emb = extract_features(info["url"])

                            if emb is None:
                                continue

                            score, avg = match_video(source_emb, emb)

                            if score > 0.65 and avg > 0.75:
                                cur.execute(
                                    "INSERT INTO matches (job_id, title, url, score) VALUES (?, ?, ?, ?)",
                                    (job_id, info["title"], url, float(score))
                                )
                                conn.commit()

                        except:
                            continue

                        processed_ids.add(vid)

                        if ts > latest_ts:
                            latest_ts = ts

            cur.execute(
                "UPDATE jobs SET latest_timestamp=? WHERE id=?",
                (latest_ts, job_id)
            )
            conn.commit()

        conn.close()
        time.sleep(30)

# ----------------------------------------
# API ROUTES
# ----------------------------------------
@app.post(
    "/upload",
    summary="Upload video",
    description="Upload a video and start detection"
)
async def upload(
    file: UploadFile = File(...),
    title: str = Form(""),
    description: str = Form(""),
    language: str = Form(""),
    country: str = Form("")
):
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    temp.write(await file.read())
    temp.close()

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO jobs (status, video_path, title, description, language, country)
        VALUES (?, ?, ?, ?, ?, ?)
    """, ("running", temp.name, title, description, language, country))

    job_id = cur.lastrowid
    conn.commit()
    conn.close()

    return {"job_id": job_id, "message": "Detection started"}


@app.get(
    "/status",
    summary="Check status",
    description="Get detection progress and matches"
)
def status(job_id: int = Query(...)):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT status FROM jobs WHERE id=?", (job_id,))
    job = cur.fetchone()

    cur.execute("SELECT title, url, score FROM matches WHERE job_id=?", (job_id,))
    matches = cur.fetchall()

    conn.close()

    return {
        "job_id": job_id,
        "status": job[0] if job else "not found",
        "matches": [
            {
                "title": m[0],
                "url": m[1],
                "score": m[2]
            } for m in matches
        ]
    }

# ----------------------------------------
# START WORKER
# ----------------------------------------
threading.Thread(target=worker_loop, daemon=True).start()

# ----------------------------------------
# RUN SERVER
# ----------------------------------------
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000)

