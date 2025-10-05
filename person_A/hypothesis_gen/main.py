from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import List, Dict, Optional
from llama3_api import generate_hypothesis_from_papers
from dotenv import load_dotenv
load_dotenv()

class Paper(BaseModel):
    id: int
    title: str
    abstract: str

class PapersRequest(BaseModel):
    papers: List[Paper]
    query: str

class HypothesisResponse(BaseModel):
    gap: str
    hypothesis: str
    evidence: List[str]
    prediction: str
    rules: List[str]
    classification: str
    further_data: str

app = FastAPI()

@app.post("/generate", response_model=HypothesisResponse)
def generate_hypothesis(request: PapersRequest) -> Dict:
    papers_list = [p.dict() for p in request.papers]
    hypothesis = generate_hypothesis_from_papers(papers_list, request.query)
    try:
        if 'gap' in hypothesis and not isinstance(hypothesis['gap'], str):
            import json as _json
            hypothesis['gap'] = _json.dumps(hypothesis['gap'], ensure_ascii=False)
        hypothesis.setdefault('hypothesis', '')
        if not isinstance(hypothesis.get('hypothesis'), str):
            hypothesis['hypothesis'] = str(hypothesis.get('hypothesis'))
        hypothesis.setdefault('evidence', [])
        if not isinstance(hypothesis.get('evidence'), list):
            hypothesis['evidence'] = [str(hypothesis.get('evidence'))]
        hypothesis.setdefault('prediction', '')
        if not isinstance(hypothesis.get('prediction'), str):
            hypothesis['prediction'] = str(hypothesis.get('prediction'))
        hypothesis.setdefault('rules', [])
        if not isinstance(hypothesis.get('rules'), list):
            hypothesis['rules'] = [str(hypothesis.get('rules'))]
        hypothesis.setdefault('classification', 'unknown')
        if not isinstance(hypothesis.get('classification'), str):
            hypothesis['classification'] = str(hypothesis.get('classification'))
        hypothesis.setdefault('further_data', 'No further insights.')
        if not isinstance(hypothesis.get('further_data'), str):
            hypothesis['further_data'] = str(hypothesis.get('further_data'))
    except Exception:
        hypothesis = {
            'gap': str(hypothesis.get('gap', '')) if isinstance(hypothesis, dict) else str(hypothesis),
            'hypothesis': str(hypothesis.get('hypothesis', '') if isinstance(hypothesis, dict) else ''),
            'evidence': hypothesis.get('evidence', []) if isinstance(hypothesis, dict) else [],
            'prediction': str(hypothesis.get('prediction', '') if isinstance(hypothesis, dict) else ''),
            'rules': hypothesis.get('rules', []) if isinstance(hypothesis, dict) else [],
            'classification': 'unknown',
            'further_data': 'Normalization failed'
        }

    return hypothesis