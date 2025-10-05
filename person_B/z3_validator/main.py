from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
from rules import z3_validate
import time
import uuid
import logging

app = FastAPI(title="Z3 Validator Service (Person B)")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("z3_validator")

class HypothesisIn(BaseModel):
    gap: Optional[str] = ""
    hypothesis: str
    evidence: Optional[List[str]] = []
    prediction: Optional[str] = ""
    rules: Optional[List[str]] = []
    classification: Optional[str] = ""
    further_data: Optional[str] = ""

class ValidationOut(BaseModel):
    gap: Optional[str] = ""
    hypothesis: str
    evidence: Optional[List[str]] = []
    prediction: Optional[str] = ""
    rules: Optional[List[str]] = []
    classification: Optional[str] = ""
    further_data: Optional[str] = ""
    validation_result: Dict

validation_logs = []

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
            "validation_result": {
                "additionalProp1": res
            }
        }
    except Exception as e:
        logger.exception("Validation failure")
        raise HTTPException(status_code=500, detail=str(e))
    latency_ms = int((time.time() - start) * 1000)
    validation_logs.append({
        "id": str(uuid.uuid4()),
        "timestamp": time.time(),
        "hypothesis": h.hypothesis,
        "result": res["valid"],
        "latency_ms": latency_ms
    })
    return response

@app.get("/logs")
def get_logs():
    return {"logs": validation_logs}