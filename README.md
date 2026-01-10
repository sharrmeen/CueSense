# CueSense — Context-Aware AI Video Editing

CueSense is a **professional-grade automated video editing system** designed to contextualize **A-roll content with relevant B-roll overlays** using a **multi-stage AI workflow**.It automates **transcription, visual analysis, contextual matching, and high-definition rendering**.

By leveraging multimodal Large Language Models (LLMs) and advanced video processing tools, it transforms raw footage into a contextually rich, edited video with minimal human intervention.

---

## The Core Intelligence: Multimodal Video Analysis
#### Before any rendering occurs, CueSense performs a deep semantic audit of all media assets to transform raw pixels into actionable metadata.
### 1. A-Roll Semantic Mapping

The system first processes the primary **talking-head (A-Roll)** footage to establish a linguistic and temporal baseline.

- **Temporal Transcription**  
  Gemini 2.5 Flash extracts the audio stream and generates a high-fidelity, word-level transcript with precise timestamps.

- **Theme Identification**  
  The AI identifies key topics, concepts, and named entities, mapping them to exact millisecond-level timecodes within the video.

- **Linguistic Anchoring**  
  This produces a semantic timeline that the Matching Agent uses to determine *exactly where* a B-roll insertion adds maximum contextual value for the viewer.
  

### 2. B-Roll Visual Inventory Indexing

Each uploaded **B-roll** clip undergoes a comprehensive visual analysis to determine its intent, content, and suitability.

- **Multimodal Frame Sampling**  
  The B-roll video is processed directly by Gemini 2.5 Flash, enabling the model to analyze visual frames over time.

- **Intent Analysis**  
  The vision model identifies objects, actions, camera perspective, and overall mood  
  *(e.g., “A high-angle shot of a chef chopping vegetables in a bright kitchen”)*.

- **Keyword Tagging**  
  A structured set of semantic keywords is generated  
  *(e.g., cooking, freshness, precision)* and persisted in **MongoDB** for fast retrieval during the matching and edit-planning phase.

---
## Preview

<img width="1280" height="800" alt="Screenshot 2026-01-11 at 3 45 11 AM" src="https://github.com/user-attachments/assets/930934b8-4d2c-4d87-ac8b-3da5c2f1357c" />
<img width="1280" height="800" alt="Screenshot 2026-01-11 at 3 46 03 AM" src="https://github.com/user-attachments/assets/0bf2a68c-e134-4355-a8b2-aa0ef974649d" />
<img width="1280" height="800" alt="Screenshot 2026-01-11 at 3 46 34 AM" src="https://github.com/user-attachments/assets/37185800-b054-45f9-bf7b-08ead58167de" />
<img width="1280" height="800" alt="Screenshot 2026-01-11 at 3 46 43 AM" src="https://github.com/user-attachments/assets/9d932333-aad4-474e-92c9-eff1d9ca80fe" />
<img width="1280" height="800" alt="Screenshot 2026-01-11 at 3 46 24 AM" src="https://github.com/user-attachments/assets/fcb117bd-89c1-4cf3-a1de-a4e3b23eb5e4" />

---

## System Architecture & Infrastructure

CueSense uses a **hybrid local + containerized architecture** to balance performance and reproducibility.

- **Docker** → Infrastructure services (MongoDB, MinIO)
- **Native execution** → Heavy compute (AI + FFmpeg) for direct hardware access

```mermaid
graph TD
    subgraph Frontend_Layer [Frontend Layer]
        React[React.js Dashboard]
        Axios[Axios Polling Client]
    end

    subgraph API_Gateway [API Gateway]
        FastAPI[FastAPI Server]
        BG_Tasks[Async Background Tasks]
    end

    subgraph AI_Engine [AI Agent Engine]
        Gemini[Gemini 2.5 Flash]
        PromptEng[Contextual Prompt Logic]
    end

    subgraph Infrastructure [Infrastructure Layer - Docker]
        Mongo[(MongoDB / Beanie)]
        MinIO[(MinIO Object Storage)]
    end

    subgraph Media_Engine [Media Engine]
        FFmpeg[FFmpeg Subprocess]
    end

    React -->|REST API| FastAPI
    FastAPI -->|CRUD Operations| Mongo
    FastAPI -->|Media Management| MinIO
    FastAPI -->|Dispatch Task| BG_Tasks
    BG_Tasks -->|Multimodal Analysis| Gemini
    BG_Tasks -->|Render Pipeline| FFmpeg
    FFmpeg -->|Stream I/O| MinIO
    Axios -->|Status Polling| FastAPI
```
## ⚙️ Technical Workflow Detail

### 1️⃣ Data Ingestion & State Management

#### Object Storage
Media assets are stored in MinIO buckets:
- `arolls`
- `brolls`
- `outputs`

#### Metadata Persistence
MongoDB + Beanie ODM track:
- project state
- timestamps
- AI-generated metadata
---

### 2️⃣ Multi-Stage AI Pipeline

CueSense orchestrates multiple specialized AI stages for high contextual relevance.

```mermaid
sequenceDiagram
    participant Worker as Background Task
    participant Gemini as Gemini 2.5 Flash
    participant DB as MongoDB

    Note over Worker, Gemini: Stage 1 — Audio Context
    Worker->>Gemini: Send A-Roll Audio
    Gemini-->>Worker: JSON Transcript + Timestamps
    Worker->>DB: Persist Transcript

    Note over Worker, Gemini: Stage 2 — Visual Inventory
    loop For each B-Roll
        Worker->>Gemini: Analyze Video Frames
        Gemini-->>Worker: Visual Metadata (Keywords / Descriptions)
        Worker->>DB: Store B-Roll Analysis
    end

    Note over Worker, Gemini: Stage 3 — Edit Plan
    Worker->>Gemini: Transcript + B-Roll Library
    Gemini-->>Worker: Edit Plan (Insert Points & Durations)
    Worker->>DB: Save Final JSON Plan
```

## Setup & Installation
### 1. Infrastructure (Docker)
#### Initialize the database and storage services:

```
docker-compose up -d
```

### 2. Environment Configuration
#### Create a .env file in the backend root. You can use the provided .env.example as a template to ensure all required variables are present.


```
GEMINI_API_KEY=your_key_here
MINIO_ENDPOINT=localhost:9000
MONGO_URI=mongodb://localhost:27017
```
### 3. Execution

#### Backend: 
```
uvicorn app.main:app --reload
```

#### Frontend: 
```
npm install && npm start
```
