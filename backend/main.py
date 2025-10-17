from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from person_A.ingest_search.embeddings import semantic_search
from person_A.hypothesis_gen.llama3_api import generate_hypothesis_from_papers
from person_B.z3_validator.rules import z3_validate
from person_B.experiment_design.exp_llama3_api import call_llama3_for_experiment
import json, time, uuid, logging
from person_A.hypothesis_gen.main import Paper, PapersRequest, HypothesisResponse
from person_B.z3_validator.main import HypothesisIn, ValidationOut

app = FastAPI(title="Neuro Research Backend")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("neuro_backend")
logs = []

@app.get("/search")
def search_papers(query: str = Query(...)) -> Dict[str, object]:
    papers = semantic_search(query)
    return {"papers": papers, "query": query}

@app.post("/generate", response_model=HypothesisResponse)
def generate_hypothesis(request: PapersRequest) -> Dict:
    papers_list = [p.dict() for p in request.papers]
    hypothesis = generate_hypothesis_from_papers(papers_list, request.query)
    try:
        if 'gap' in hypothesis and not isinstance(hypothesis['gap'], str):
            hypothesis['gap'] = json.dumps(hypothesis['gap'], ensure_ascii=False)
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

@app.post("/validate", response_model=ValidationOut)
def validate(h: HypothesisIn):
    start = time.time()
    try:
        res = z3_validate(h.hypothesis, h.rules, h.classification, h.further_data)
        response = {
            "gap": h.gap,
            "hypothesis": h.hypothesis,
            "evidence": h.evidence,
            "prediction": h.prediction,
            "rules": h.rules,
            "classification": h.classification,
            "further_data": h.further_data,
            "validation_result": {"additionalProp1": res}
        }
    except Exception as e:
        logger.exception("Validation failure")
        raise HTTPException(status_code=500, detail=str(e))
    latency_ms = int((time.time() - start) * 1000)
    logs.append({
        "id": str(uuid.uuid4()),
        "timestamp": time.time(),
        "hypothesis": h.hypothesis,
        "result": res["valid"],
        "latency_ms": latency_ms,
        "endpoint": "validate"
    })
    return response

@app.post("/design")
def design_experiment(v: HypothesisIn):
    start = time.time()
    hypothesis = v.hypothesis
    try:
        hypothesis_text = f"{v.hypothesis}\nRules: {', '.join(v.rules)}\nClassification: {v.classification}\nFurther Data: {v.further_data}"
        text = call_llama3_for_experiment(hypothesis_text)
        try:
            exp_json = json.loads(text)
        except Exception:
            exp_json = None
    except Exception as e:
        logger.warning("LLaMA call failed or not available; using fallback template. Error: %s", e)
        exp_json = None
    if exp_json is None:
        outcome_measures = []
        if "plaque" in hypothesis.lower() or "amyloid" in hypothesis.lower():
            outcome_measures.append("Amyloid plaque staining (IHC)")
        if "cogn" in hypothesis.lower() or "memory" in hypothesis.lower():
            outcome_measures.append("Behavioral tests (Morris water maze)")
        if "microglia" in hypothesis.lower():
            outcome_measures.append("Microglial activation markers (Iba1, CD68)")
        for rule in v.rules:
            if "inflammation" in rule.lower():
                outcome_measures.append("Inflammation markers (e.g., IL-6, TNF-alpha)")
            if "phagocytosis" in rule.lower():
                outcome_measures.append("Phagocytic activity assay")
        if not outcome_measures:
            outcome_measures = ["General histology", "Behavioral assays"]
        exp_json = {
            "model": "5xFAD transgenic mice",
            "groups": ["Control (vehicle)", "Treatment A", "Treatment B", "Combination"],
            "n_per_group": 12,
            "duration_weeks": 12,
            "treatment_route": "intraperitoneal injection",
            "outcome_measures": outcome_measures,
            "expected_result": f"Treatment groups will show improvement in {', '.join(outcome_measures)} compared to control.",
            "latex": generate_latex(hypothesis, outcome_measures)
        }
    latency_ms = int((time.time() - start) * 1000)
    logs.append({
        "id": str(uuid.uuid4()),
        "timestamp": time.time(),
        "hypothesis": hypothesis,
        "latency_ms": latency_ms,
        "endpoint": "design"
    })
    return exp_json

def generate_latex(hypothesis, outcome_measures):
    om = "\\\\ \n".join(outcome_measures)
    latex = f"""
\\section*{{Experiment Design}}
\\textbf{{Hypothesis:}} {hypothesis}
\\subsection*{{Model}}
5xFAD transgenic mice
\\subsection*{{Groups}}
Control (vehicle), Treatment A, Treatment B, Combination
\\subsection*{{Sample Size}}
12 per group
\\subsection*{{Duration}}
12 weeks
\\subsection*{{Outcome Measures}}
{om}
\\subsection*{{Expected Result}}
Treatment groups will show improvement in outcome measures compared to control.
"""
    return latex

@app.get("/logs")
def get_logs():
    return {"logs": logs}