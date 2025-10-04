import os
import json
from PyPDF2 import PdfReader

CHUNK_SIZE = 500  # words

def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + " "
    return text

def chunk_text(text, chunk_size=CHUNK_SIZE):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunks.append(" ".join(words[i:i+chunk_size]))
    return chunks

def preprocess_pdfs(pdf_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    paper_id = 0
    for pdf_file in os.listdir(pdf_dir):
        if pdf_file.endswith(".pdf"):
            text = extract_text_from_pdf(os.path.join(pdf_dir, pdf_file))
            chunks = chunk_text(text)
            with open(os.path.join(output_dir, f"{pdf_file}.json"), "w") as f:
                json.dump({"id": paper_id, "title": pdf_file, "chunks": chunks}, f)
            paper_id += 1