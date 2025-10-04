from fastapi import FastAPI, Query
from typing import List, Dict
from embeddings import semantic_search

app = FastAPI(title="Ingest & Search Service", port=8000)

@app.get("/search")
def search_papers(query: str = Query(...)) -> Dict[str, List[Dict]]:
    papers = semantic_search(query)
    return {"papers": papers}

# Run: uvicorn main:app --host 0.0.0.0 --port 8000