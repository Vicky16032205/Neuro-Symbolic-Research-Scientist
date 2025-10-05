from parser import preprocess_pdfs
from embeddings import create_embeddings

if __name__ == "__main__":
    preprocess_pdfs("person_A/data", "person_A/chunks")
    create_embeddings("person_A/chunks")
    print("✅ Data ingestion complete. You can now run the API service.")
