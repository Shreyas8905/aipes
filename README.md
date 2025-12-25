# AI PPT Evaluation Orchestration Layer of HackOps

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
2.  **Specialization:** A "Vision Agent" critiques design while a "Logic Agent" critiques the business model.
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
