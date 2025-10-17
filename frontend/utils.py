import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import json, os, time, logging
from typing import List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cerebro_pipeline")

# Use Docker service name 'backend' and port 8000
BASE_URL = os.getenv("BACKEND_URL", "http://backend:8000")
SEARCH_URL = f"{BASE_URL}/search"
GENERATE_URL = f"{BASE_URL}/generate"
VALIDATE_URL = f"{BASE_URL}/validate"
DESIGN_URL = f"{BASE_URL}/design"

session = requests.Session()
retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
session.mount("http://", HTTPAdapter(max_retries=retries))
session.mount("https://", HTTPAdapter(max_retries=retries))

def call_search(query: str, top_k: int = 3) -> Dict:
    start_time = time.time()
    try:
        r = session.get(SEARCH_URL, params={"query": query, "top_k": top_k}, timeout=30)
        r.raise_for_status()
        response = r.json()
        logger.info(f"Search completed in {time.time() - start_time:.2f}s")
        return {"response": response, "latency": time.time() - start_time}
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise ValueError(f"Search service error: {str(e)}")

def call_generate(papers: List[Dict], query: str = "") -> Dict:
    start_time = time.time()
    try:
        payload = {"papers": papers, "query": query}
        r = session.post(GENERATE_URL, json=payload, timeout=60)
        r.raise_for_status()
        response = r.json()
        expected_fields = ["gap", "hypothesis", "evidence", "prediction", "rules", "classification", "further_data"]
        if not all(field in response for field in expected_fields):
            missing = [f for f in expected_fields if f not in response]
            raise ValueError(f"Missing expected fields in hypothesis response: {missing}")
        logger.info(f"Hypothesis generation completed in {time.time() - start_time:.2f}s")
        return {"response": response, "latency": time.time() - start_time}
    except Exception as e:
        logger.error(f"Hypothesis generation failed: {e}")
        raise ValueError(f"Generate service error: {str(e)}")

def call_validate(hypothesis_json: Dict) -> Dict:
    start_time = time.time()
    try:
        r = session.post(VALIDATE_URL, json=hypothesis_json, timeout=60)
        r.raise_for_status()
        response = r.json()
        expected_fields = ["gap", "hypothesis", "evidence", "prediction", "rules", "classification", "further_data", "validation_result"]
        if not all(field in response for field in expected_fields):
            missing = [f for f in expected_fields if f not in response]
            raise ValueError(f"Missing expected fields in validation response: {missing}")
        if "additionalProp1" not in response.get("validation_result", {}):
            raise ValueError("Validation response missing 'validation_result.additionalProp1'")
        logger.info(f"Validation completed in {time.time() - start_time:.2f}s")
        return {"response": response, "latency": time.time() - start_time}
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        raise ValueError(f"Validate service error: {str(e)}")

def call_design(validated_hypothesis: Dict) -> Dict:
    start_time = time.time()
    try:
        r = session.post(DESIGN_URL, json=validated_hypothesis, timeout=90)
        r.raise_for_status()
        response = r.json()
        expected_fields = ["model", "groups", "n_per_group", "duration_weeks", "treatment_route", "outcome_measures", "expected_result"]
        if not all(field in response for field in expected_fields):
            missing = [f for f in expected_fields if f not in response]
            raise ValueError(f"Missing expected fields in design response: {missing}")
        logger.info(f"Experiment design completed in {time.time() - start_time:.2f}s")
        return {"response": response, "latency": time.time() - start_time}
    except Exception as e:
        logger.error(f"Experiment design failed: {e}")
        raise ValueError(f"Design service error: {str(e)}")