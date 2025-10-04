import json
import os

def chunk_text(text: str, size: int = 200) -> list:
    """
    Break text into fixed-size chunks (toy version).
    """
    return [text[i:i+size] for i in range(0, len(text), size)]

def save_mock_db(chunks: list, path: str):
    """
    Save chunks into JSON mock DB.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump([{"id": i, "text": chunk} for i, chunk in enumerate(chunks)], f, indent=2)