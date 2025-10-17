# 🧠 Neuro-Symbolic AI Scientist Agent
This project implements a distributed AI Research Scientist designed to accelerate discovery in fields like Alzheimer’s disease (AD) by generating, validating, and designing scientifically rigorous, actionable experiments.

## 🎯 Project Goal
To automate the full scientific discovery process—from literature retrieval to laboratory blueprint—by combining the creative intuition of Large Language Models (LLMs) with the logical rigor of Symbolic AI.

--------------------------------------------------------------------------------
## ✨ Key Features & Innovation

| Feature | Description | Sources |
|---|---|---|
| **Scientific Rigor (The Symbolic Edge)** | Hypotheses are formally validated using the **Z3 SMT Solver** to check for logical inconsistencies against a knowledge base of known AD facts (e.g., Aβ clearance does not guarantee cognitive improvement). | |
| **Actionable Output** | The system generates a comprehensive **Experiment Blueprint** (including required models like **5xFAD mice**, detailed treatment groups, specific outcome measures like **Morris water maze**, and duration). The output is available as JSON, LaTeX, and PDF. | |
| **Scalable Architecture** | Built on **4 core microservices** using Docker and FastAPI, enabling parallel development and independent testing. All communication uses **JSON over HTTP**. | |
| **Advanced LLM Integration** | Leverages **LLaMA 3** (via the Cerebras API) as the "neural brain" for both creative hypothesis generation (identifying knowledge gaps) and structured experiment synthesis. | |
| **Professional Demo** | A central **Streamlit Dashboard** (Port 8501) orchestrates the entire pipeline, visually displaying the step-by-step process from query to final blueprint. | |

--------------------------------------------------------------------------------
## 🏗️ Architecture and Workflow Pipeline

The pipeline is split between two roles: Person A (Neural Intelligence) and Person B (Symbolic & Interface).

| Step | Service Name (Port) | Owner Role | Purpose & Technology |
|---|---|---|---|
| 1. Retrieval | `ingest-search (8000)` | Person A | Finds the top 3 relevant Alzheimer’s papers based on a user query using semantic search (FAISS/Chroma). |
| 2. Generation | `hypothesis-gen (8001)` | Person A | Identifies a knowledge gap and proposes a testable hypothesis (e.g., "Combining X with Y will improve Z outcomes") using LLaMA 3. |
| 3. Validation | `z3-validator (8002)` | Person B | Checks if the hypothesis logically contradicts known biological facts defined in the knowledge base using the Z3 SMT Solver. |
| 4. Design | `experiment-design (8003)` | Person B | Converts the validated hypothesis into a detailed experimental blueprint using LLaMA 3. |
| Interface | `dashboard (8501)` | Person B | Streamlit UI that calls all services sequentially and displays the final result and download options. |

--------------------------------------------------------------------------------
## 🚀 Getting Started

Prerequisites

- Docker Desktop (with Docker Compose)
- Git
- Optional (for local development without Docker): Python 3.10+ and a virtual environment manager

Required environment variables

- CEREBRAS_API_KEY — access for LLaMA 3 (Cerebras)
- PINECONE_API_KEY — (optional) Pinecone index key used by the ingest/search code

Create an example `.env`

Copy the included `.env.example` to `.env` and populate your keys:

```
# .env (example)
CEREBRAS_API_KEY=your_cerebras_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
# Optional override used by frontend when running outside Docker
BACKEND_URL=http://localhost:8000
```

Run with Docker (recommended)

1. From the repository root, build and start the services using Docker Compose (this will build the `backend` and `frontend` images defined in the repo):

```
# Build and run in detached mode
docker compose up --build -d

# Confirm containers are running
docker compose ps
```

2. Open the Streamlit dashboard in your browser:

```
http://localhost:8501
```

3. Follow logs (optional):

```
# Dashboard logs (frontend)
docker compose logs -f frontend

# Backend logs
docker compose logs -f backend
```

4. To stop and remove containers:

```
docker compose down
```

Run locally without Docker (developer mode) — Windows PowerShell

1. Create and activate a virtual environment then install dependencies. There are `requirements.txt` files for backend and frontend; install both:

```
# from repo root
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt
```

2. Export environment variables (PowerShell):

```
$env:CEREBRAS_API_KEY = "your_cerebras_api_key_here"
$env:PINECONE_API_KEY = "your_pinecone_api_key_here"
$env:BACKEND_URL = "http://localhost:8000"
```

3. Start backend (FastAPI)

```
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

4. Start frontend (Streamlit) in a separate terminal

```
cd frontend
streamlit run app.py --server.port 8501
```

Tips and troubleshooting

- If LLaMA/Cerebras API keys are missing the services will attempt safe fallbacks, but hypothesis generation or experiment design may return template responses.
- On Windows you may need to install Visual C++ build tools for the `z3-solver` package.
- The Docker Compose file exposes `backend` on port 8000 and `frontend` on port 8501. If these ports are in use, update `docker-compose.yml` and the `BACKEND_URL` environment variable accordingly.

Helper scripts

- `dev_start.ps1` — helper to build and start the Docker Compose stack.
- `dev_stop.ps1` — stops and removes the stack.

If you'd like, I can also add a GitHub Actions workflow that builds the images and runs a quick smoke test.
