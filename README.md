<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #111; max-width: 900px; margin: auto; padding: 20px;">

<h1>Aegis Labs: Architectural Overview and Methodological Framework</h1>

<h2>3. Ingestion and Feature Extraction Pipeline</h2>

<p>The system converts temporal visual data into high-dimensional mathematical representations.</p>

<ul>
<li><strong>Tensor Normalization:</strong> Frames are resized to 
\(224 \times 224\) pixels and normalized.</li>
<li><strong>Vector Embedding Generation:</strong> Embeddings are normalized using 
\(L_2\) normalization, projecting them onto a unit hypersphere.</li>
</ul>

<h2>6. Structural Similarity and Scoring Methodology</h2>

<p><strong>Cosine Similarity Matrix:</strong></p>

<p>
Let \( S \) represent the matrix of source embeddings and \( T \) represent the matrix of target embeddings.
</p>

<p style="text-align:center; font-size: 18px;">
\[
M = T \cdot S^T
\]
</p>

<p>
Because the vectors are \(L_2\) normalized, this directly yields cosine similarity.
</p>

<p><strong>Final Confidence Score:</strong></p>

<p style="text-align:center; font-size: 18px;">
\[
\text{Score} = \left(\frac{\text{Strong Matches}}{\text{Total Frames}}\right) \times \text{Average Similarity}
\]
</p>

<h2>7. Robustness Considerations</h2>

<ul>
<li>Supports transformations such as compression and scaling</li>
<li>Handles moderate cropping via semantic embeddings</li>
<li>Threshold tuning allows precision/recall balancing</li>
</ul>

<h2>Credits</h2>

<ul>
<li>A product by <strong><a href="https://emogi.space">Team Emogi</a></strong></li>
<li>Hackathon Team Name: "Quantum Stack"</li>
</ul>

</body>
