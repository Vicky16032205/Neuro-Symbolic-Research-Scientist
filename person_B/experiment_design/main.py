# person_b/experiment_design/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import json
import logging
import time, uuid
import llama3_api

app = FastAPI(title="Experiment Design Service (Person B)")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("experiment_design")

design_logs = []

class ValidationInfo(BaseModel):
    gap: Optional[str] = ""
    hypothesis: str
    evidence: Optional[List[str]] = []
    prediction: Optional[str] = ""
    validation_result: Optional[Dict] = None
    rules: Optional[List[str]] = []
    classification: Optional[str] = ""
    further_data: Optional[str] = ""


@app.post("/design")
def design_experiment(v: ValidationInfo):
    start = time.time()
    hypothesis = v.hypothesis
    try:
        hypothesis_text = f"{v.hypothesis}\nRules: {', '.join(v.rules)}\nClassification: {v.classification}\nFurther Data: {v.further_data}"
        text = llama3_api.call_llama3_for_experiment(hypothesis_text)
        try:
            exp_json = json.loads(text)
        except Exception:
            exp_json = None
    except Exception as e:
        logger.warning("LLaMA call failed or not available; using fallback template. Error: %s", e)
        exp_json = None

    if exp_json is None:
        # Fallback template generator
        outcome_measures = []
        if "plaque" in hypothesis.lower() or "amyloid" in hypothesis.lower():
            outcome_measures.append("Amyloid plaque staining (IHC)")
        if "cogn" in hypothesis.lower() or "memory" in hypothesis.lower():
            outcome_measures.append("Behavioral tests (Morris water maze)")
        if "microglia" in hypothesis.lower():
            outcome_measures.append("Microglial activation markers (Iba1, CD68)")
        # Use dynamic rules to refine outcome measures
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
    design_logs.append({
        "id": str(uuid.uuid4()),
        "timestamp": time.time(),
        "hypothesis": hypothesis,
        "latency_ms": latency_ms
    })
    return exp_json

@app.get("/logs")
def get_logs():
    return {"logs": design_logs}

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