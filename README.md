<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #111; max-width: 900px; margin: auto; padding: 20px;">

<h1>Aegis Labs</h1>

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
The system is based on the research paper:
</p>

<p>
📄 <strong>
<a href="https://github.com/Imimi328/Aegis-Labs/blob/main/Documentation/Continuous%20Sematic%20Vide%20Threat%20Detection.pdf" target="_blank">
Continuous Semantic Video Threat Detection
</a>
</strong>
</p>

<p>
This paper outlines the theoretical framework, embedding strategy, and similarity computation methodology used within Aegis Labs.
</p>

<hr>

<h2>3. Core Architectural Design</h2>

<ul>
<li><strong>ASGI Web Interface:</strong> Built using FastAPI, enabling high-performance asynchronous request handling and non-blocking endpoints.</li>

<li><strong>State Management Engine:</strong> SQLite3 is used as a persistent datastore, functioning as a lightweight job queue and lifecycle manager.</li>

<li><strong>Asynchronous ML Worker:</strong> A continuously running background worker processes jobs without reliance on external brokers such as Redis or RabbitMQ.</li>
</ul>

<hr>

<h2>4. Ingestion and Feature Extraction Pipeline</h2>

<ol>
<li>
<strong>Frame Extraction and Sampling:</strong> Approximately 12 frames are sampled uniformly across the video duration to preserve temporal diversity.
</li>

<li>
<strong>Tensor Normalization:</strong> Frames are resized to <strong>224 × 224 pixels</strong> and converted from BGR to RGB format.
</li>

<li>
<strong>Vector Embedding Generation:</strong> The system utilizes Google's SigLIP model to generate high-dimensional embeddings. 
These vectors undergo L2 normalization, projecting them onto a unit hypersphere for efficient cosine similarity computation.
</li>
</ol>

<hr>

<h2>5. Adaptive Query Generation (LLM Integration)</h2>

<ul>
<li><strong>LLM Engine:</strong> Gemma 4 E4B is used for intelligent query generation.</li>

<li><strong>Semantic Expansion:</strong> Automatically generates variations such as highlights, edits, clips, shorts, reuploads, and transformed titles.</li>

<li><strong>Structured Output:</strong> Produces strictly formatted JSON arrays to ensure deterministic downstream processing.</li>
</ul>

<hr>

<h2>6. Global Network Telemetry and Scraping</h2>

<ul>
<li><strong>Heuristic + Semantic Querying:</strong> Combines static keyword search with AI-generated queries using yt-dlp.</li>

<li><strong>In-Memory Processing:</strong> Video streams are processed directly in memory, eliminating disk I/O bottlenecks.</li>
</ul>

<hr>

<h2>7. Structural Similarity and Scoring Methodology</h2>

<h3>Cosine Similarity Matrix</h3>
<p>
Let <strong>S</strong> represent the source embedding matrix and <strong>T</strong> represent the target embedding matrix.
</p>

<p style="text-align:center; font-weight: bold;">
M = T × S<sup>T</sup>
</p>

<p>
Due to L2 normalization, this operation directly computes cosine similarity between all frame pairs.
</p>

<h3>Max-Pooling Aggregation</h3>
<p>
For each target frame, the maximum similarity score across all source frames is selected.
</p>

<h3>Confidence Score Calculation</h3>

<p style="text-align:center; font-weight: bold;">
Score = (Strong Matches / Total Frames) × Average Similarity
</p>

<p>
A "strong match" is defined as a similarity score greater than 0.85.
</p>

<h3>Violation Detection Criteria</h3>

<ul>
<li>Score &gt; 0.65</li>
<li>Average Similarity &gt; 0.75</li>
</ul>

<p>
Videos meeting these thresholds are flagged as potential intellectual property violations.
</p>

<hr>

<h2>8. Example Video</h2>

<p>
The following test video demonstrates the system's input format:
</p>

<video width="100%" controls>
  <source src="https://github.com/Imimi328/Aegis-Labs/blob/main/Videos/Test.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

<p>
🔗 Direct Link: 
<a href="https://github.com/Imimi328/Aegis-Labs/blob/main/Videos/Test.mp4" target="_blank">
View on GitHub
</a>
</p>

<hr>

<h2>9. Robustness Considerations</h2>

<ul>
<li><strong>Compression Resilience:</strong> Maintains stability under re-encoding and bitrate variation.</li>
<li><strong>Partial Cropping Tolerance:</strong> Semantic embeddings allow detection despite moderate spatial alterations.</li>
<li><strong>Threshold Adaptability:</strong> System thresholds can be tuned for precision-recall optimization.</li>
</ul>

<hr>

<h2>10. System Limitations</h2>

<ul>
<li>No temporal sequence alignment</li>
<li>No audio fingerprinting integration</li>
<li>Sequential processing limits horizontal scalability</li>
</ul>

<hr>

<h2>11. Future Work</h2>

<ul>
<li>Segment-based temporal alignment</li>
<li>Multi-crop embedding strategies</li>
<li>Distributed worker architecture (multi-node scaling)</li>
<li>Audio-visual fusion detection</li>
</ul>

<hr>

<h2>📄 Credits</h2>

<ul>
<li>A product by <strong><a href="https://emogi.space" target="_blank">Team Emogi</a></strong></li>
<li>Hackathon Team Name: <strong>Quantum Stack</strong></li>
</ul>

</body>
