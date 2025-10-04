# person_b/dashboard/utils.py
import requests
import json
from typing import List, Dict

# Person A endpoints (adjust host if remote)
SEARCH_URL = "http://127.0.0.1:8000/search"
GENERATE_URL = "http://127.0.0.1:8001/generate"
VALIDATE_URL = "http://127.0.0.1:8002/validate"
DESIGN_URL = "http://127.0.0.1:8003/design"

def call_search(query, top_k=3):
    r = requests.get(SEARCH_URL, params={"query": query, "top_k": top_k}, timeout=30)
    r.raise_for_status()
    return r.json()

# def call_generate(papers):
#     # API expects list of papers
#     payload = {"papers": papers}
#     r = requests.post(GENERATE_URL, json=payload, timeout=60)
#     r.raise_for_status()
#     return r.json()


def call_generate(papers):
    # API expects list of papers
    payload = {"papers": papers}
    r = requests.post(GENERATE_URL, json=payload, timeout=60)
    r.raise_for_status()
    response = r.json()
    # Validate expected fields
    expected_fields = ["gap", "hypothesis", "evidence", "prediction", "rules", "classification", "further_data"]
    if not all(field in response for field in expected_fields):
        missing = [f for f in expected_fields if f not in response]
        raise ValueError(f"Missing expected fields in hypothesis response: {missing}")
    return response




def call_validate(hypothesis_json):
    # hypothesis_json = {gap, hypothesis, evidence, prediction}
    print(hypothesis_json)
    r = requests.post(VALIDATE_URL, json=hypothesis_json, timeout=30)
    r.raise_for_status()
    return r.json()

def call_design(validated_hypothesis):
    # validated_hypothesis includes hypothesis + validation_result maybe
    r = requests.post(DESIGN_URL, json=validated_hypothesis, timeout=60)
    r.raise_for_status()
    return r.json()