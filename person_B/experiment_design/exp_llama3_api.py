import os
from cerebras.cloud.sdk import Cerebras
from dotenv import load_dotenv

load_dotenv()

def call_llama3_for_experiment(hypothesis_text: str) -> str:
    """
    Use Cerebras SDK to call LLaMA 3.1 8B and generate an experiment plan as JSON text.
    """
    api_key = os.getenv("CEREBRAS_API_KEY")
    if not api_key:
        raise RuntimeError("CEREBRAS_API_KEY environment variable is not set")

    client = Cerebras(api_key=api_key)

    prompt = f"""
You are an expert preclinical neuroscientist. Convert this validated hypothesis and associated metadata into a structured experiment plan.

Input:
{hypothesis_text}

Return JSON exactly with keys:
model, groups, n_per_group, duration_weeks, treatment_route, outcome_measures, expected_result, latex
Use the provided rules, classification, and further data to refine outcome measures and expected results.
"""

    response = client.chat.completions.create(
        model="llama3.1-8b",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=600
    )

    try:
        generated = response.choices[0].message.content
    except (AttributeError, IndexError, KeyError):
        import json
        generated = json.dumps(response.to_dict() if hasattr(response, 'to_dict') else response, default=str, indent=2)

    return generated