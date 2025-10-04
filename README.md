# CerebroDiscover — Neuro-Symbolic Research Scientist (Alzheimer's)

This repository contains several small services and a Streamlit dashboard that together form a research-assistant pipeline for hypothesis generation, symbolic validation, and experiment design.

Services
- `person_A/ingest_search` — FastAPI service exposing `/search` (port 8000)
- `person_A/hypothesis_gen` — FastAPI service exposing `/generate` (port 8001)
- `person_B/z3_validator` — FastAPI service exposing `/validate` (port 8002)
- `person_B/experiment_design` — FastAPI service exposing `/design` (port 8003)
- `person_B/dashboard` — Streamlit app that orchestrates the pipeline

Quick start (dev)
1. Copy environment variables template:

   Copy `.env.example` to `.env` and fill in API keys.

2. Install dependencies (use a virtualenv / conda):

   See `requirements.txt` — install via pip.

3. Start services (one terminal per service) or use the provided `dev_start.ps1` PowerShell script for local development.

Service run commands (examples)

PowerShell examples (one service per terminal):

```powershell
# In person_A/ingest_search
cd person_A/ingest_search
uvicorn main:app --host 127.0.0.1 --port 8000 --reload

# In person_A/hypothesis_gen
cd person_A/hypothesis_gen
uvicorn main:app --host 127.0.0.1 --port 8001 --reload

# In person_B/z3_validator
cd person_B/z3_validator
uvicorn main:app --host 127.0.0.1 --port 8002 --reload

# In person_B/experiment_design
cd person_B/experiment_design
uvicorn main:app --host 127.0.0.1 --port 8003 --reload

# Start dashboard
cd person_B/dashboard
streamlit run app.py
```

Notes
- The dashboard (`person_B/dashboard/app.py`) calls the four services on localhost ports 8000–8003. If you change ports, update `person_B/dashboard/utils.py`.
- Large ML deps (torch, transformers, sentence-transformers) may take time and require appropriate platforms (CPU/GPU). `z3-solver` is a compiled package and may require Visual C++ build tools on Windows if a binary wheel is not available.
- Two external API keys are expected in the codebase and should be set in `.env`:
  - `CEREBRAS_API_KEY` — used by LLaMA calls in `hypothesis_gen` and `experiment_design` modules
  - `PINECONE_API_KEY` — used by the embeddings/indexing module in `person_A/ingest_search`

Safety / local dev hints
- If you don't have access to Cerebras, `person_B/experiment_design/main.py` and `person_A/hypothesis_gen/` include fallback behavior (template or heuristic) when the LLM call fails.

Contact
- If you want I can add a `.env.example`, dev-start scripts, and a few smoke tests next. Tell me which you'd prefer.
