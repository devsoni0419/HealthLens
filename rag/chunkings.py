import json
import nltk
from pathlib import Path

nltk.download("punkt")

INPUT_FILE = "data/processed/unified_docs.jsonl"
OUTPUT_FILE = "data/processed/chunks.jsonl"

Path("data/processed").mkdir(parents=True, exist_ok=True)

def chunk_text(text, max_tokens=400):
    sentences = nltk.sent_tokenize(text)
    chunks = []
    current = ""

    for sentence in sentences:
        if len(current) + len(sentence) < max_tokens:
            current += " " + sentence
        else:
            chunks.append(current.strip())
            current = sentence

    if current:
        chunks.append(current.strip())

    return chunks

def create_chunks():
    with open(INPUT_FILE, "r", encoding="utf-8") as f_in, \
         open(OUTPUT_FILE, "w", encoding="utf-8") as f_out:

        for line in f_in:
            doc = json.loads(line)
            chunks = chunk_text(doc["content"])

            for i, chunk in enumerate(chunks):
                chunk_doc = {
                    "chunk_id": f"{doc['doc_id']}_chunk_{i}",
                    "doc_id": doc["doc_id"],
                    "source": doc["source"],
                    "title": doc["title"],
                    "content": chunk,
                    "metadata": doc["metadata"]
                }

                f_out.write(json.dumps(chunk_doc) + "\n")

if __name__ == "__main__":
    create_chunks()
