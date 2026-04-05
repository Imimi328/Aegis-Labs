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
import re
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
LLM_MODEL = "gemma-4-e4b-it"

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
            outputs = vision_model.vision_model(**inputs)
            image_embeds = outputs.pooler_output
            image_embeds = image_embeds / image_embeds.norm(dim=-1, keepdim=True)

        embs.append(image_embeds.cpu().numpy())

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
    short_desc = description[:300] if description else ""

    prompt = f"""
You are an expert at finding pirated, reuploaded, or unauthorized fan content on YouTube.
Based on the original video details below, generate 10 highly realistic YouTube search queries that a human would actually type to find clips, AMVs, edits, or full reuploads of this video.

Original Video Title: {title}
Description Snippet: {short_desc}
Language: {language}
Country: {country}

STRICT RULES:
1. DO NOT append technical words like "reupload", "detection", or "check" to the queries.
2. Think like a fan or pirate. Add modifiers they actually use, such as: "AMV", "reaction", "full scene", "best moments", "lyrics", "sub", "dub", "clip", "shorts", "edit", "live".
3. Use realistic variations of the title (e.g., drop punctuation, use abbreviations).
4. Return exactly 10 queries.

Return ONLY a valid JSON array of strings.
"""

    try:
        print("\n[DEBUG] Asking LLM for search queries...")
        res = requests.post(
            LLM_API_URL,
            headers={"Content-Type": "application/json"},
            json={
                "model": LLM_MODEL,
                "messages": [
                    {
                        "role": "system", 
                        "content": "You are a backend API. You output raw, valid JSON arrays of strings. No markdown formatting, no conversational filler."
                    },
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7
            },
            timeout=60
        )

        if res.status_code != 200:
            print(f"[ERROR] LLM API returned: {res.status_code} - {res.text}")
            return [title]

        data = res.json()
        text = data["choices"][0]["message"]["content"].strip()
        
        match = re.search(r'\[.*\]', text, re.DOTALL)
        
        if match:
            clean_json = match.group(0)
            queries = json.loads(clean_json)
            print(f"[DEBUG] LLM generated {len(queries)} queries successfully.")
            return queries
        else:
            print("[DEBUG] Could not find a JSON array in the LLM response.")
            return [title]

    except Exception as e:
        print("LLM parsing error:", e)
        return [title]

# ----------------------------------------
# WORKER LOOP
# ----------------------------------------
def worker_loop():
    print("\n[WORKER] Worker thread started. Scanning for jobs...")
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
            
            # The timestamp from the last time we ran this job
            db_latest_ts = job[7] 
            
            # A temporary tracker for the newest video we find in THIS run
            new_highest_ts = db_latest_ts

            print(f"\n==============================================")
            print(f"[WORKER] Processing Job ID {job_id}: '{title}'")
            print(f"==============================================")
            
            print(f"[DEBUG] Extracting baseline features for local video...")
            source_emb = extract_features(video_path)
            if source_emb is None:
                print(f"[ERROR] Failed to extract features from local video.")
                continue
            print(f"[DEBUG] Baseline features extracted successfully.")

            queries = generate_queries(title, description, language, country)

            with yt_dlp.YoutubeDL(ydl_opts()) as ydl:
                for q in queries:
                    print(f"\n[SEARCH] -> Executing YouTube search for: '{q}'")
                    try:
                        data = ydl.extract_info(f"ytsearch10:{q}", download=False)
                    except Exception as e:
                        print(f"[ERROR] yt-dlp search failed for '{q}': {e}")
                        continue

                    entries = data.get("entries", [])
                    print(f"[SEARCH] -> Found {len(entries)} videos. Analyzing...")

                    for e in entries:
                        if not e:
                            continue

                        vid = e.get("id")
                        if not vid or vid in processed_ids:
                            continue

                        ts = e.get("timestamp", 0)
                        
                        # Compare against the static DB timestamp. 
                        # (If db_latest_ts is 0, this is our very first sweep, so check everything!)
                        if ts <= db_latest_ts and db_latest_ts != 0:
                            print(f"  [SKIP] {vid} is older than our last sweep.")
                            continue

                        url = f"https://www.youtube.com/watch?v={vid}"
                        vid_title = e.get('title', 'Unknown Title')
                        
                        print(f"  [CHECKING] {vid_title} ({url})")

                        try:
                            # Getting direct stream URL to extract frames
                            info = ydl.extract_info(url, download=False)
                            if "url" not in info:
                                print(f"    -> [WARN] No direct stream URL found, skipping.")
                                continue
                            
                            # Stream the video over the network to grab frames
                            emb = extract_features(info["url"])

                            if emb is None:
                                print(f"    -> [WARN] Could not extract frames.")
                                continue

                            score, avg = match_video(source_emb, emb)
                            print(f"    -> SigLIP Similarity: {score:.2f} (Avg Frame Sim: {avg:.2f})")

                            if score > 0.65 and avg > 0.75:
                                print(f"    -> 🚨 [MATCH FOUND!] Saving to database.")
                                cur.execute(
                                    "INSERT INTO matches (job_id, title, url, score) VALUES (?, ?, ?, ?)",
                                    (job_id, info["title"], url, float(score))
                                )
                                conn.commit()

                        except Exception as ex:
                            print(f"    -> [ERROR] Failed during analysis: {ex}")
                            continue

                        processed_ids.add(vid)

                        # Update our temporary tracker if we found a newer video
                        if ts > new_highest_ts:
                            new_highest_ts = ts

            print(f"\n[WORKER] Finished current loop for Job ID {job_id}.")
            
            # Now that the loop is totally done, update the database clock for the NEXT time it runs
            cur.execute(
                "UPDATE jobs SET latest_timestamp=? WHERE id=?",
                (new_highest_ts, job_id)
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
