import chromadb
import json
from sentence_transformers import SentenceTransformer

CHROMA_PATH = "data/chroma_db"
INPUT_FILE = "data/processed/chunks.jsonl"

client = chromadb.PersistentClient(path=CHROMA_PATH)

collection = client.get_or_create_collection(
    name="healthlens",
    metadata={"hnsw:space": "cosine"}
)

def build_vector_store():
    model = SentenceTransformer("all-MiniLM-L6-v2")

    ids = []
    documents = []
    metadatas = []

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            item = json.loads(line)

            ids.append(item["chunk_id"])
            documents.append(item["content"])

            clean_meta = {}
            for k, v in item["metadata"].items():
                if isinstance(v, list):
                    clean_meta[k] = ", ".join(v)
                else:
                    clean_meta[k] = v

            metadatas.append(clean_meta)

    embeddings = model.encode(documents, show_progress_bar=True)

    batch_size = 5000

    for i in range(0, len(ids), batch_size):
        collection.add(
            ids=ids[i:i+batch_size],
            documents=documents[i:i+batch_size],
            embeddings=embeddings[i:i+batch_size],
            metadatas=metadatas[i:i+batch_size]
        )

    print("Chroma index built successfully")


def search(query, top_k=5):
    model = SentenceTransformer("all-MiniLM-L6-v2")

    query_embedding = model.encode([query])

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k
    )

    return results


if __name__ == "__main__":
    build_vector_store()
