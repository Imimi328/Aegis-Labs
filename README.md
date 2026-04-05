<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #111; max-width: 900px; margin: auto; padding: 20px;">

<h1>Aegis Labs</h1>

<h2>🎥 System Demonstration</h2>

<p>
The following demonstration video provides a high-level overview of Aegis Labs in operation, including ingestion, 
analysis, and detection workflow.
</p>

[![Aegis Labs Demo](https://img.youtube.com/vi/GR_q2VrB-cQ/0.jpg)](https://www.youtube.com/watch?v=GR_q2VrB-cQ)

<hr>

<h2>1. System Overview</h2>
<p>
Aegis Labs is a proprietary threat intelligence and digital media authentication system designed for continuous detection 
of unauthorized video redistribution. The platform focuses on identifying intellectual property violations, particularly 
within sports and high-value broadcast media, through a scalable and asynchronous processing architecture.
</p>

<p>
The system integrates multimodal artificial intelligence, combining computer vision embeddings with adaptive natural 
language query generation to perform semantic-level video matching across global platforms.
</p>

<hr>

<h2>2. Research Foundation</h2>

<p>
📄 <strong>
<a href="https://raw.githubusercontent.com/Imimi328/Aegis-Labs/main/Documentation/Continuous%20Sematic%20Vide%20Threat%20Detection.pdf" target="_blank">
Continuous Semantic Video Threat Detection (Research Paper)
</a>
</strong>
</p>

<p>
This document provides the theoretical and methodological foundation of the system, including embedding strategies, 
similarity modeling, and detection thresholds.
</p>

<hr>

<h2>3. Core Architectural Design</h2>

<ul>
<li><strong>ASGI Web Interface:</strong> Built using FastAPI for high-performance asynchronous request handling.</li>

<li><strong>State Management Engine:</strong> SQLite3 serves as a lightweight persistent queue and lifecycle manager.</li>

<li><strong>Asynchronous ML Worker:</strong> Background processing without external brokers, ensuring system simplicity.</li>
</ul>

<hr>

<h2>4. Ingestion and Feature Extraction Pipeline</h2>

<ol>
<li>
<strong>Frame Extraction:</strong> ~12 frames sampled uniformly across video duration.
</li>

<li>
<strong>Normalization:</strong> Frames resized to <strong>224 × 224</strong> and converted to RGB.
</li>

<li>
<strong>Embedding Generation:</strong> SigLIP embeddings with L2 normalization for cosine similarity computation.
</li>
</ol>

<hr>

<h2>5. Adaptive Query Generation</h2>

<ul>
<li><strong>Model:</strong> Gemma 4 E4B</li>
<li><strong>Function:</strong> Semantic expansion (clips, highlights, edits, reuploads)</li>
<li><strong>Output:</strong> Structured JSON for deterministic processing</li>
</ul>

<hr>

<h2>6. Network Telemetry</h2>

<ul>
<li>Hybrid heuristic + AI querying using yt-dlp</li>
<li>Full in-memory video processing (no disk I/O overhead)</li>
</ul>

<hr>

<h2>7. Similarity & Detection Model</h2>

<p style="text-align:center; font-weight: bold;">
M = T × S<sup>T</sup>
</p>

<ul>
<li>Max similarity per frame (max-pooling)</li>
<li>Strong match threshold: > 0.85</li>
<li>Final Score = (Strong Matches / Total Frames) × Average Similarity</li>
</ul>

<p><strong>Detection Conditions:</strong></p>
<ul>
<li>Score &gt; 0.65</li>
<li>Average Similarity &gt; 0.75</li>
</ul>

<hr>

<h2>8. Robustness</h2>

<ul>
<li>Compression-resistant</li>
<li>Handles partial cropping</li>
<li>Adjustable detection thresholds</li>
</ul>

<hr>

<h2>9. Limitations</h2>

<ul>
<li>No temporal alignment</li>
<li>No audio analysis</li>
<li>Limited scalability (single worker)</li>
</ul>

<hr>

<h2>10. Future Work</h2>

<ul>
<li>Temporal sequence modeling</li>
<li>Multi-crop embeddings</li>
<li>Distributed processing architecture</li>
<li>Audio-visual fusion</li>
</ul>

<hr>

<h2>📄 Credits</h2>

<ul>
<li>A product by <strong><a href="https://emogi.space" target="_blank">Team Emogi</a></strong></li>
<li>Hackathon Team: <strong>Quantum Stack</strong></li>
</ul>

</body>
