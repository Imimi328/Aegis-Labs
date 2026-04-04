<div style="max-width: 800px; margin: 0 auto; font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #18181b; padding: 2rem;">

<h1 style="font-size: 2.25rem; font-weight: 700; margin-bottom: 0.5rem; letter-spacing: -0.025em;">Aegis Labs: Digital Asset Protection 🛡️</h1>
<p style="font-size: 1.125rem; color: #52525b; margin-top: 0; margin-bottom: 1.5rem;">
    <strong>Powered by <a href="https://emogi.space" target="_blank" style="color: #09090b; text-decoration: underline;">emogi.space</a></strong>
</p>

<p style="margin-bottom: 2rem;">
    A private, internal tool designed to authenticate digital sports media and detect unauthorized redistribution across global networks using AI fingerprinting.
</p>

<hr style="border: none; border-top: 1px solid #e4e4e7; margin: 2rem 0;">

<h2 style="font-size: 1.5rem; font-weight: 600; margin-bottom: 1rem;">🚀 Core Capabilities</h2>
<ul style="padding-left: 1.5rem; margin-bottom: 2rem;">
    <li style="margin-bottom: 0.5rem;"><strong>Video Fingerprinting:</strong> Generates AI embeddings from proprietary video assets using CLIP (ViT-B-32).</li>
    <li style="margin-bottom: 0.5rem;"><strong>Network Scraping:</strong> Automatically searches public networks (via <code>yt-dlp</code>) for potential matches.</li>
    <li style="margin-bottom: 0.5rem;"><strong>Similarity Matching:</strong> Compares structural data to flag misappropriated clips based on confidence thresholds.</li>
    <li style="margin-bottom: 0.5rem;"><strong>Threat Dashboard:</strong> A minimalist frontend interface to upload assets and review flagged content.</li>
</ul>

<hr style="border: none; border-top: 1px solid #e4e4e7; margin: 2rem 0;">

<h2 style="font-size: 1.5rem; font-weight: 600; margin-bottom: 1rem;">🛠️ Internal Stack</h2>

<ul style="padding-left: 1.5rem; margin-bottom: 2rem;">
    <li style="margin-bottom: 0.5rem;"><strong>Backend Engine:</strong> FastAPI, PyTorch (OpenCLIP), OpenCV, SQLite3, and yt-dlp.</li>
    <li style="margin-bottom: 0.5rem;"><strong>Frontend Client:</strong> Single-file HTML5, Vanilla JavaScript, and Tailwind CSS.</li>
</ul>

<hr style="border: none; border-top: 1px solid #e4e4e7; margin: 2rem 0;">

<h2 style="font-size: 1.5rem; font-weight: 600; margin-bottom: 1rem;">⚙️ Quick Start (Local Use)</h2>

<p style="margin-bottom: 1rem;">1. Start the internal backend engine:</p>
<pre style="background-color: #f4f4f5; padding: 1rem; border-radius: 0.5rem; overflow-x: auto; margin-bottom: 1.5rem;"><code style="font-family: 'JetBrains Mono', monospace; font-size: 0.875rem; color: #27272a;">python emogi_server.py</code></pre>

<p style="margin-bottom: 1rem;">2. Open the dashboard:</p>
<p style="margin-bottom: 2rem; color: #52525b;">Simply double-click the <code>index.html</code> file to open it in your browser. Ensure the <code>API_BASE</code> variable inside the file points to your local server address (e.g., <code>http://localhost:3000</code>).</p>

<hr style="border: none; border-top: 1px solid #e4e4e7; margin: 2rem 0;">

<h2 style="font-size: 1.5rem; font-weight: 600; margin-bottom: 1rem;">📄 Credits</h2>
<ul style="padding-left: 1.5rem; margin-bottom: 2rem; color: #52525b;">
    <li style="margin-bottom: 0.5rem;">Concept, Architecture, and Design by <strong><a href="https://emogi.space" style="color: #09090b; text-decoration: underline;">emogi.space</a></strong>.</li>
</ul>
</div>
