# from fastapi import FastAPI, Request
# from pydantic import BaseModel
# from typing import List, Dict
# from llama3_api import generate_hypothesis_from_papers
# from dotenv import load_dotenv
# load_dotenv()

# class Paper(BaseModel):
#     id: int
#     title: str
#     abstract: str

# class PapersRequest(BaseModel):
#     papers: List[Paper]

# app = FastAPI()

# @app.post("/generate")
# def generate_hypothesis(request: PapersRequest) -> Dict:
#     papers_list = [p.dict() for p in request.papers]
#     hypothesis = generate_hypothesis_from_papers(papers_list)
#     return hypothesis







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

# Define the response model to include new fields
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
    hypothesis = generate_hypothesis_from_papers(papers_list)
    return hypothesis