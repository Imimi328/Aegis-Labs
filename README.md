<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #111; max-width: 900px; margin: auto; padding: 20px;">

<h1>Aegis Labs: Architectural Overview and Methodological Framework</h1>

<h2>1. System Overview</h2>
<p>
Aegis Labs constitutes a proprietary threat intelligence system designed for the proactive authentication of digital media assets. 
The platform mitigates intellectual property violations—specifically the unauthorized redistribution of sports media—by deploying a scalable, 
asynchronous pipeline that combines computer vision, natural language processing, and structural similarity analysis.
</p>

<p>
The system leverages modern multimodal intelligence, integrating Google-based vision embeddings and lightweight large language models 
for adaptive query generation.
</p>

<hr>

<h2>2. Core Architectural Design</h2>

<ul>
<li><strong>ASGI Web Interface:</strong> Built on FastAPI, handling asynchronous client I/O and exposing non-blocking endpoints.</li>

<li><strong>State Management Engine:</strong> SQLite3 is used as a persistent datastore, acting as a queue manager for job lifecycle tracking.</li>

<li><strong>Asynchronous ML Worker:</strong> A daemonized Python thread continuously processes jobs in the background without requiring external brokers.</li>
</ul>

<hr>

<h2>3. Ingestion and Feature Extraction Pipeline</h2>

<ol>
<li>
<strong>Frame Extraction and Sampling:</strong> The system samples approximately 12 frames uniformly across the video duration to maintain temporal representation.
</li>

<li>
<strong>Tensor Normalization:</strong> Frames are resized to <strong>224 × 224 pixels</strong> and converted from BGR to RGB format before processing.
</li>

<li>
<strong>Vector Embedding Generation:</strong> The system uses Google's SigLIP model to generate embeddings. 
These embeddings are normalized using L2 normalization, projecting them onto a unit hypersphere for efficient similarity comparison.
</li>
</ol>

<hr>

<h2>4. Adaptive Query Generation (LLM Integration)</h2>

<ul>
<li><strong>LLM Engine:</strong> Uses Gemma 4 E4B for generating intelligent search queries.</li>

<li><strong>Semantic Expansion:</strong> Generates variations such as highlights, clips, edits, shorts, and reuploads.</li>

<li><strong>Structured Output:</strong> Returns strictly formatted JSON arrays for deterministic integration.</li>
</ul>

<hr>

<h2>5. Global Network Telemetry and Scraping</h2>

<ul>
<li><strong>Heuristic + Semantic Querying:</strong> Uses yt-dlp with both static and AI-generated queries.</li>

<li><strong>In-Memory Processing:</strong> Video streams are processed directly without disk storage, reducing I/O overhead.</li>
</ul>

<hr>

<h2>6. Structural Similarity and Scoring Methodology</h2>

<h3>Cosine Similarity Matrix</h3>
<p>
Let S represent the source embedding matrix and T represent the target embedding matrix.
</p>

<p style="text-align:center; font-weight: bold;">
M = T × S<sup>T</sup>
</p>

<p>
Since all vectors are L2 normalized, this directly computes cosine similarity between frames.
</p>

<h3>Max-Pooling Aggregation</h3>
<p>
For each target frame, the maximum similarity score against all source frames is selected.
</p>

<h3>Confidence Score Calculation</h3>

<p style="text-align:center; font-weight: bold;">
Score = (Number of Strong Matches / Total Frames) × Average Similarity
</p>

<p>
Where a "strong match" is defined as a similarity score greater than 0.85.
</p>

<h3>Violation Detection</h3>
<p>
If:
</p>

<ul>
<li>Score &gt; 0.65</li>
<li>Average Similarity &gt; 0.75</li>
</ul>

<p>
The video is flagged as a potential intellectual property violation.
</p>

<hr>

<h2>7. Robustness Considerations</h2>

<ul>
<li><strong>Compression Resilience:</strong> Stable under re-encoding and bitrate changes.</li>
<li><strong>Partial Cropping Tolerance:</strong> Detects moderate cropping using semantic embeddings.</li>
<li><strong>Threshold Adaptability:</strong> Adjustable thresholds allow tuning between precision and recall.</li>
</ul>

<hr>

<h2>8. System Limitations and Future Work</h2>

<ul>
<li>No temporal alignment (frame order not modeled)</li>
<li>No audio fingerprinting</li>
<li>Sequential processing limits scalability</li>
</ul>

<p><strong>Future Improvements:</strong></p>

<ul>
<li>Segment-based temporal matching</li>
<li>Multi-crop embedding strategy</li>
<li>Distributed worker architecture</li>
</ul>

<hr>

<h2>📄 Credits</h2>

<ul>
<li>A product by <strong><a href="https://emogi.space">Team Emogi</a></strong></li>
<li>Hackathon Team Name: "Quantum Stack"</li>
</ul>

</body>
