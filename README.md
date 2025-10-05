
# Neuro-Symbolic Research Scientist — Alzheimer's AI

This project is a modular pipeline for neuro-symbolic research on Alzheimer's disease, combining LLM-driven hypothesis generation, symbolic validation, and experiment design. It features:

- **FastAPI microservices** for ingest/search, hypothesis generation, symbolic validation, and experiment design
- **Streamlit dashboard** for orchestration and visualization

## Project Structure

- `person_A/ingest_search` — `/search` API (port 8000)
- `person_A/hypothesis_gen` — `/generate` API (port 8001)
- `person_B/z3_validator` — `/validate` API (port 8002)
- `person_B/experiment_design` — `/design` API (port 8003)
- `person_B/dashboard` — Streamlit UI (calls all services)

## Getting Started

1. **Clone repo & set up environment**
   - Copy `.env.example` to `.env` and add your API keys
   - Install dependencies: `pip install -r requirements.txt`

2. **Run services** (each in a separate terminal, or use `dev_start.ps1`):
   ```powershell
   # Ingest/Search
   cd person_A/ingest_search; uvicorn main:app --host 127.0.0.1 --port 8000 --reload
   # Hypothesis Generation
   cd person_A/hypothesis_gen; uvicorn main:app --host 127.0.0.1 --port 8001 --reload
   # Symbolic Validation
   cd person_B/z3_validator; uvicorn main:app --host 127.0.0.1 --port 8002 --reload
   # Experiment Design
   cd person_B/experiment_design; uvicorn main:app --host 127.0.0.1 --port 8003 --reload
   # Dashboard
   cd person_B/dashboard; streamlit run app.py
   ```

## Configuration

- Set `CEREBRAS_API_KEY` and `PINECONE_API_KEY` in `.env`
- Ports: 8000–8003 (update in `dashboard/utils.py` if changed)
- ML dependencies may require CPU/GPU; `z3-solver` may need Visual C++ build tools on Windows

## Developer Notes

- Modular, service-oriented architecture for rapid prototyping
- Fallback logic for LLM calls if API keys are missing
- Data and chunk files in `person_A/data` and `person_A/chunks`

---
For issues, feature requests, or contributions, open a GitHub issue or pull request.
