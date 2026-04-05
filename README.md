# Aegis Labs: Architectural Overview and Methodological Framework

## 1. System Overview

Aegis Labs constitutes a proprietary threat intelligence system designed for the proactive authentication of digital media assets. The platform mitigates intellectual property violations—specifically the unauthorized redistribution of sports media—by deploying a scalable, asynchronous pipeline that combines computer vision, natural language processing, and structural similarity analysis.

The system has been upgraded to leverage modern multimodal intelligence, incorporating Google’s vision-language embedding models and lightweight local large language models for adaptive query generation.

---

## 2. Core Architectural Design

The system architecture is strictly decoupled into three primary strata: an ASGI web interface, an embedded relational state manager, and an asynchronous machine-learning telemetry worker.

* **ASGI Web Interface:** Built upon the FastAPI framework, this layer handles asynchronous client I/O. It exposes non-blocking endpoints for asset ingestion and status polling, isolating the client from the computationally expensive machine-learning pipeline.
* **State Management Engine:** SQLite3 is utilized as the persistent data store. It acts as an embedded queue management system, tracking job lifecycles (`running`, `completed`) and persisting similarity metrics for historical auditing.
* **Asynchronous ML Worker:** A persistent, daemonized Python thread continuously polls the state manager. Upon detecting an active job, it locks the database row and initiates the extraction, indexing, and scoring pipelines entirely in the background, circumventing the need for external message brokers such as Redis or RabbitMQ.

---

## 3. Ingestion and Feature Extraction Pipeline

The core of the detection mechanism relies on converting temporal visual data into high-dimensional mathematical representations.

1. **Frame Extraction and Sampling:** Upon asset ingestion, the system utilizes OpenCV to read the video buffer. To ensure computational efficiency while maintaining temporal representation, the engine uniformly samples a fixed number of frames (typically 12) across the asset's duration.
2. **Tensor Normalization:** Extracted frames are downscaled to a resolution of $224 \times 224$ pixels and converted from BGR to RGB color space. These images are subsequently passed through a preprocessing pipeline to construct normalized tensors suitable for neural network ingestion.
3. **Vector Embedding Generation:** The system leverages SigLIP, a modern vision-language model developed by Google. Unlike traditional contrastive models, SigLIP employs a sigmoid-based loss function, resulting in improved embedding alignment and robustness under transformations such as compression, scaling, and partial cropping. The model maps visual input into a dense latent space, and all embeddings undergo $L_2$ normalization to enable efficient cosine similarity computation.

---

## 4. Adaptive Query Generation (LLM Integration)

To enhance detection coverage beyond naive keyword matching, the system integrates a lightweight large language model.

* **LLM Engine:** Query generation is powered by Gemma 4 E4B, a compact and efficient model developed by Google.
* **Semantic Expansion:** Given the original video metadata (title, description, language, country), the model generates semantically enriched search queries, including variations such as highlights, clips, edits, shorts, and reuploads.
* **Structured Output:** The model is constrained to return strictly formatted JSON arrays, ensuring deterministic integration with the scraping pipeline.

---

## 5. Global Network Telemetry and Scraping

To identify unauthorized distribution, the system executes active telemetry across public network indices.

* **Heuristic + Semantic Querying:** The worker thread utilizes `yt-dlp` to execute both heuristic and LLM-generated search queries (e.g., `ytsearch10:<query>`), significantly increasing recall across diverse content variations.
* **In-Memory Stream Processing:** To mitigate I/O bottlenecks and localized storage constraints, target candidate videos are not written to disk. Instead, stream URLs are dynamically extracted and piped directly into the OpenCV instance for immediate frame sampling and embedding generation.

---

## 6. Structural Similarity and Scoring Methodology

The identification of misappropriated assets is treated as a high-dimensional nearest-neighbor problem, resolved through matrix operations and bipartite thresholding.

1. **Cosine Similarity Matrix:** Let $S$ represent the matrix of source embeddings and $T$ represent the matrix of candidate target embeddings. The similarity matrix $M$ is computed via:
   (M = T \cdot S^T)
   Given prior $L_2$ normalization, this directly yields cosine similarity scores.
2. **Max-Pooling Feature Aggregation:** For each target frame, the system extracts the maximum similarity score against all source frames, forming a vector of peak correspondences.
3. **Bipartite Threshold Evaluation:** A statistical evaluation determines match strength. A "strong match" threshold (e.g., $M_{ij} > 0.85$) is applied. The final confidence score is computed as:
   (\text{Score} = \left(\frac{\text{Strong Matches}}{\text{Total Frames}}\right) \times \text{Average Similarity})
4. **Violation Flagging:** If composite thresholds are exceeded (e.g., $\text{Score} > 0.65$ and $\text{Average} > 0.75$), the candidate is flagged as a likely intellectual property violation.

---

## 7. Robustness Considerations

The system is designed to tolerate real-world transformations commonly observed in unauthorized reuploads:

* **Resilience to Compression:** Embedding normalization ensures stability across re-encoded media.
* **Partial Cropping Tolerance:** Semantic embeddings enable detection under moderate spatial cropping, though extreme crops may reduce confidence.
* **Adaptive Thresholding:** Matching thresholds can be tuned dynamically to balance precision and recall depending on deployment requirements.

---

## 8. System Limitations and Future Work

While effective, the current implementation exhibits several limitations:

* Lack of temporal alignment (frame order not explicitly modeled)
* Absence of audio fingerprinting
* Sequential processing bottlenecks in high-load scenarios

Future iterations will incorporate:

* Segment-based temporal matching
* Multi-crop embedding strategies for enhanced robustness
* Distributed worker architecture for horizontal scalability

---

<h2 style="font-size: 1.5rem; font-weight: 600; margin-bottom: 1rem;">📄 Credits</h2>
<ul style="padding-left: 1.5rem; margin-bottom: 2rem; color: #52525b;">
    <li style="margin-bottom: 0.5rem;">A product by <strong><a href="https://emogi.space" style="color: #09090b; text-decoration: underline;">Team Emogi</a></strong>.</li>
    <li style="margin-bottom: 0.5rem;">Hackathon Team Name: "Quantum Stack".</li>
</ul>
