# Aegis Labs: Architectural Overview and Methodological Framework

## 1. System Overview
Aegis Labs constitutes a proprietary threat intelligence system designed for the proactive authentication of digital media assets. The platform mitigates intellectual property violations—specifically the unauthorized redistribution of sports media—by deploying a scalable, asynchronous pipeline that combines computer vision, natural language processing, and structural similarity analysis.

## 2. Core Architectural Design
The system architecture is strictly decoupled into three primary strata: an ASGI web interface, an embedded relational state manager, and an asynchronous machine-learning telemetry worker.

*   **ASGI Web Interface:** Built upon the FastAPI framework, this layer handles asynchronous client I/O. It exposes non-blocking endpoints for asset ingestion and status polling, isolating the client from the computationally expensive machine-learning pipeline.
*   **State Management Engine:** SQLite3 is utilized as the persistent data store. It acts as an embedded queue management system, tracking job lifecycles (`queued`, `processing`, `done`) and persisting similarity metrics for historical auditing.
*   **Asynchronous ML Worker:** A persistent, daemonized Python thread continuously polls the state manager. Upon detecting a queued job, it locks the database row and initiates the extraction, indexing, and scoring pipelines entirely in the background, circumventing the need for external message brokers such as Redis or RabbitMQ.

## 3. Ingestion and Feature Extraction Pipeline
The core of the detection mechanism relies on converting temporal visual data into high-dimensional mathematical representations.

1.  **Frame Extraction and Sampling:** Upon asset ingestion, the system utilizes OpenCV to read the video buffer. To ensure computational efficiency while maintaining temporal representation, the engine uniformly samples exactly 12 frames across the asset's duration.
2.  **Tensor Normalization:** Extracted frames are downscaled to a resolution of $224 \times 224$ pixels and converted from BGR to RGB color space. These images are subsequently passed through a preprocessing pipeline to construct normalized tensors suitable for neural network ingestion.
3.  **Vector Embedding Generation:** The system leverages OpenAI's Contrastive Language-Image Pre-training (CLIP) architecture, specifically the Vision Transformer base model with 32-pixel patches (`ViT-B-32`). The model acts as a zero-shot image encoder, mapping the visual input into a dense latent space. To facilitate efficient downstream similarity calculations, the resulting embeddings undergo $L_2$ normalization, projecting them onto a unit hypersphere.

## 4. Global Network Telemetry and Scraping
To identify unauthorized distribution, the system executes active telemetry across public network indices.

*   **Heuristic Querying:** The worker thread utilizes `yt-dlp` to execute heuristic searches (e.g., `ytsearch10:"sports highlights"`) against target platforms, bypassing official API rate limits and accessing raw distribution channels.
*   **In-Memory Stream Processing:** To mitigate I/O bottlenecks and localized storage constraints, target candidate videos are not written to disk. Instead, stream URLs are dynamically extracted and piped directly into the OpenCV instance for immediate frame sampling and embedding generation.

## 5. Structural Similarity and Scoring Methodology
The identification of misappropriated assets is treated as a high-dimensional nearest-neighbor problem, resolved through matrix operations and bipartite thresholding.

1.  **Cosine Similarity Matrix:** Let $S$ represent the matrix of source embeddings and $T$ represent the matrix of candidate target embeddings. The similarity matrix $M$ is computed via the dot product of the target embeddings and the transposed source embeddings: 
    $$M = T \cdot S^T$$
    Because the vectors are previously $L_2$ normalized, this operation directly yields the cosine similarity for every frame pair.
2.  **Max-Pooling Feature Aggregation:** For each target frame, the system isolates the highest similarity score against any source frame, generating a one-dimensional array of maximum frame scores.
3.  **Bipartite Threshold Evaluation:** A rigid statistical evaluation determines the final flag status. The system defines a "strong match" threshold (e.g., $M_{ij} > 0.85$). The final confidence metric is derived from the product of the ratio of strong matches to total frames and the overall average match score. 
4.  **Violation Flagging:** If the composite metrics exceed defined heuristic boundaries (e.g., $\text{Score} > 0.65$ and $\text{Average} > 0.75$), the candidate asset is definitively flagged as an intellectual property violation and logged into the persistent state manager.

<ul style="padding-left: 1.5rem; margin-bottom: 2rem; color: #52525b;">
    <li style="margin-bottom: 0.5rem;">A product by <strong><a href="https://emogi.space" style="color: #09090b; text-decoration: underline;">Team Emogi</a></strong>.</li>
</ul>
