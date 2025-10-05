import os
import json
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = "neuro-scientist"
pc = Pinecone(api_key=PINECONE_API_KEY)
model = SentenceTransformer("stsb-roberta-large")

def initialize_index():
    desired_dim = model.get_sentence_embedding_dimension()
    if INDEX_NAME not in pc.list_indexes().names():
        pc.create_index(
            name=INDEX_NAME,
            dimension=desired_dim,
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )
    return pc.Index(INDEX_NAME)

index = initialize_index()

def create_embeddings(json_dir):
    for json_file in os.listdir(json_dir):
        if json_file.endswith(".json"):
            with open(os.path.join(json_dir, json_file), "r") as f:
                data = json.load(f)
                chunks = data["chunks"]
                embeddings = model.encode(chunks).tolist()
                vectors = [
                    {
                        "id": f"{data['id']}_{idx}",
                        "values": embeddings[idx],
                        "metadata": {
                            "title": data["title"],
                            "paper_id": data["id"],
                            "chunk_idx": idx,
                            "text": chunk
                        }
                    }
                    for idx, chunk in enumerate(chunks)
                ]
                index.upsert(vectors=vectors)
    print("All embeddings upserted to Pinecone.")

def semantic_search(query, top_k=6):
    query_emb = model.encode([query]).tolist()[0]
    result = index.query(
        vector=query_emb,
        top_k=top_k,
        include_metadata=True
    )

    papers = []
    seen_papers = set()
    for match in result["matches"]:
        meta = match["metadata"]
        pid = meta["paper_id"]
        if pid not in seen_papers:
            papers.append({
                "id": pid,
                "title": meta["title"],
                "abstract": meta["text"][:300] + "..."
            })
            seen_papers.add(pid)
    return papers