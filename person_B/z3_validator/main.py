# person_b/z3_validator/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
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

class ValidationOut(BaseModel):
    valid: bool
    reason: str
    proof_trace: List[str]
    warnings: Optional[List[str]] = []

# Simple in-memory logs (for demo); use persistent store for production
validation_logs = []

@app.post("/validate", response_model=ValidationOut)
def validate(h: HypothesisIn):
    start = time.time()
    try:
        res = z3_validate(h.hypothesis)
    except Exception as e:
        logger.exception("Validation failure")
        raise HTTPException(status_code=500, detail=str(e))
    latency_ms = int((time.time() - start) * 1000)
    # append log
    validation_logs.append({
        "id": str(uuid.uuid4()),
        "timestamp": time.time(),
        "hypothesis": h.hypothesis,
        "result": res["valid"],
        "latency_ms": latency_ms
    })
    return res

@app.get("/logs")
def get_logs():
    return {"logs": validation_logs}