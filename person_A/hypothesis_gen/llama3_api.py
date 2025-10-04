import os
import requests
import json
import re
from dotenv import load_dotenv

load_dotenv()

CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY")
API_URL = "https://api.cerebras.ai/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {CEREBRAS_API_KEY}",
    "Content-Type": "application/json"
}

def fix_json_with_llm(raw_text):
    prompt = f"""
You are a helpful assistant. Convert the following text into a valid JSON object with keys: gap, hypothesis, evidence (list), prediction. Only return the JSON object.
Text:
{raw_text}
"""
    payload = {
        "model": "llama3.1-8b",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 300,
        "temperature": 0.0
    }
    resp = requests.post(API_URL, headers=HEADERS, json=payload, timeout=30)
    print("Fix JSON LLM response:", resp.status_code, resp.text)
    resp.raise_for_status()
    content = resp.json().get("choices", [])[0].get("message", {}).get("content", "")
    try:
        return json.loads(content)
    except Exception as e:
        print("Final JSON decode error:", e)
        return {"error": "Could not decode JSON after fix", "raw": content}

def generate_hypothesis_from_papers(papers):
    papers_str = "\n".join(
        [f"Title: {p['title']}\nAbstract: {p['abstract']}" for p in papers]
    )
    prompt = f"""
You are a neuroscientist. Read these paper summaries and generate a hypothesis about Alzheimer's:
{papers_str}

Return ONLY a valid JSON object with the following keys: gap, hypothesis, evidence (list), prediction.
Do not include any explanation, markdown, or text outside the JSON. Your entire response must be a single JSON object.
"""
    payload = {
        "model": "llama3.1-8b",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 500,
        "temperature": 0.7
    }
    resp = requests.post(API_URL, headers=HEADERS, json=payload, timeout=30)
    print("Cerebras response:", resp.status_code, resp.text)
    resp.raise_for_status()
    content = resp.json().get("choices", [])[0].get("message", {}).get("content", "")

    # Try direct JSON parsing first
    try:
        return json.loads(content)
    except Exception as e:
        print("Direct JSON decode error:", e)
        # fallback: try to extract JSON object using regex
        match = re.search(r"({.*})", content, re.DOTALL)
        if match:
            json_str = match.group(1)
            try:
                return json.loads(json_str)
            except Exception as e:
                print("Regex JSON decode error:", e)
                # If still fails, use LLM to fix
                return fix_json_with_llm(json_str)
        # If no JSON found, use LLM to fix the whole content
        return fix_json_with_llm(content)
