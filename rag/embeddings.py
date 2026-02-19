from sentence_transformers import SentenceTransformer
import json
import numpy as np

MODEL_NAME = "all-MiniLM-L6-v2"

model = SentenceTransformer(MODEL_NAME)

def generate_embeddings(input_file):
    texts = []
    metadata = []

    with open(input_file, "r", encoding="utf-8") as f:
        for line in f:
            item = json.loads(line)
            texts.append(item["content"])
            metadata.append(item)

    embeddings = model.encode(texts, show_progress_bar=True)

    return embeddings, metadata
