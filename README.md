# AIPES

## 1. Introduction

**AIPES** (AI Powered Evaluation System) is a production-grade orchestration layer designed to automate the evaluation of pitch decks (PPTs) for hackathons and startup competitions. By leveraging a **Multi-Agent Architecture**, AIPES analyzes both the **visual quality** (slides, layout, aesthetics) and the **content logic** (feasibility, problem-solution fit) of a presentation simultaneously.

This system is designed to be the "Brain" of the **HackOps** platform, capable of processing hundreds of submissions in parallel without human intervention, providing unbiased, detailed scorecards in seconds.

---

## 2. Problem & Solution

### The Problem

- **Scale:** Hackathons often receive 500+ PDF submissions in hours.
- **Bottleneck:** Human judges cannot physically read every slide in detail within a short timeframe.
- **Bias:** Human grading is subjective and fatigues over time.
- **Idle Resources:** Sequential processing leaves powerful AI models sitting idle while waiting for file I/O.

### The Solution

AIPES implements a **Multi-Agent LangGraph Workflow** orchestrated by an asynchronous queuing system:

1.  **Parallelism:** Unlike linear scripts, AIPES splits the PDF into visual and text streams.
2.  **Specialization:** A "Vision Agent" critiques design while a "Logic Agent" critiques the technicalities & business model.
3.  **Synthesis:** A final "Judge Agent" aggregates these findings into a 0-20 score with reasoning.

---

## 3. System Architecture

![AIPES Architecture](https://github.com/Shreyas8905/aipes/blob/main/dia.png)

_Note: The database and cloudinary part needs to be implemented during deployment._

---

## 4. Key Features

### 🚀 High-Performance Queuing System

The core differentiator of AIPES is its **"No Agent Sits Idle"** policy.

- **Concurrency Control:** Uses `asyncio.Semaphore` to manage throughput. If the system is set to process 5 files at once, it will strictly maintain 5 active agents. As soon as one finishes, the next file in the queue is instantly picked up.
- **Non-Blocking I/O:** File downloads (from Cloudinary/DB) happen asynchronously, ensuring the GPU-intensive AI agents are constantly fed data.

### 🧩 Modular "Plug-and-Play" Architecture

The system follows strict software engineering principles (Single Responsibility Principle):

- **Interface-Driven Loading:** The `loader.py` module is an interface. You can switch from a **Local Folder Scan** to a **Cloudinary Database Fetch** by changing just _one line of code_ in `main.py`.
- **Agnostic Processing:** The AI Core (`ai_engine.py`) does not care where the file comes from, only that it has a path. This makes the system ready for deployment with minimal changes.

---

## 5. Technology Stack

| Technology    | Usage                     |
| :------------ | :------------------------ |
| **Python**    | Core Language             |
| **FastAPI**   | REST API & Async Server   |
| **LangGraph** | Multi-Agent Orchestration |
| **Groq**      | Ultra-fast LLM Inference  |
| **PyMuPDF**   | High-speed PDF Extraction |
| **Pydantic**  | Data Validation & Schema  |

![Backend](https://skillicons.dev/icons?i=py,fastapi)

---

## 6. Project Directory Structure

```text
ppt_eval_system/
├── test_ppts/             # Local storage for PDF files (Input Source)
│   ├── Team_Alpha.pdf
│   └── Team_Beta.pdf
├── temp_images/           # Temporary storage for extracted slide images
├── ai_engine.py           # The "Brain": LangGraph Agent Logic
├── queue_service.py       # The "Manager": Concurrency & Queuing Logic
├── loader.py              # The "Fetcher": Handles file ingestion (Local/Cloud/DB)
├── main.py                # The "Gateway": FastAPI Application Entry Point
├── requirements.txt       # Python dependencies
└── .env                   # Environment variables (API Keys)
```

### File Explanations

* **`main.py`**: The entry point. It initializes the FastAPI server, connects the `Loader` and the `Queue`, and exposes the REST endpoints (e.g., `/test_pipeline`).
* **`ai_engine.py`**: Contains the **LangGraph** workflow. It defines the Agents (Extractor, Design, Content, Scorer) and the Pydantic models for structured JSON output.
* **`queue_service.py`**: Manages the `asyncio` event loop. It accepts a list of files and processes them in parallel batches (defined by `concurrency_limit`), handling errors gracefully so one bad file doesn't crash the server.
* **`loader.py`**: A modular class that fetches files. Currently set to `BatchLoader` (Local), but designed to be easily swapped for `DatabaseLoader` or `CloudinaryLoader`.

---

## 7. How to Run

### Prerequisites
* Python 3.9+
* A Groq API Key

### Step 1: Installation
Clone the repository and install dependencies:

```bash
pip install -r requirements.txt
```

### Step 2: Configuration

Create a `.env` file in the root directory:

```plaintext
GROQ_API_KEY=gsk_your_api_key_here
```

### Step 3: Add Data

Place your Pitch Deck PDFs into the `test_ppts/` folder.

### Step 4: Run Server

Start the FastAPI server:

```bash
uvicorn main:app --reload
```

### Step 5: Trigger Evaluation

Open your browser or Postman and hit:
`http://127.0.0.1:8000/test_pipeline`

You will see the logs processing files in parallel, and the final response will be a JSON object containing scores and reasoning for every team.

---


#### Quick Note

The api endpoint here is open ended and accepts requests from all origins. For this system to be used with backend, proper cors handling must be done for security purpose. Still being faster than traditional scipts based system, the time required for processing will differ from resource to resource and number of PPTs queued. Hence proper time out must be set based on the requirements.

---

## 8. Conclusion

AIPES transforms the subjective, time-consuming task of pitch deck evaluation into an objective, data-driven process. By combining the speed of **Groq**, the structure of **LangGraph**, and the concurrency of **FastAPI**, this system provides a scalable backend solution for modern HackOps platforms.
