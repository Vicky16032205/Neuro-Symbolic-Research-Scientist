from fastapi import FastAPI, Query
from typing import List, Dict
from embeddings import semantic_search

app = FastAPI(title="Ingest & Search Service", port=8000)


@app.get("/search")
def search_papers(query: str = Query(...)) -> Dict[str, object]:
    """Perform semantic search and return both the papers and the original query.

    Returning the query lets downstream services (e.g. /generate) accept the
    search output directly without missing required fields.
    """
    papers = semantic_search(query)
    return {"papers": papers, "query": query}