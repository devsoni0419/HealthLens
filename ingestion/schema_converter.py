import json
from pathlib import Path

INPUT_FILE = "data/medline_clean.jsonl"
OUTPUT_FILE = "data/processed/unified_docs.jsonl"

Path("data/processed").mkdir(parents=True, exist_ok=True)

def convert():
    with open(INPUT_FILE, "r", encoding="utf-8") as f_in, \
         open(OUTPUT_FILE, "w", encoding="utf-8") as f_out:

        for line in f_in:
            item = json.loads(line)

            unified = {
                "doc_id": f"medline_{item['topic_id']}",
                "source": "NIH Medline",
                "title": item.get("title", ""),
                "content": item.get("summary", ""),
                "metadata": {
                    "topic_id": item.get("topic_id"),
                    "mesh_terms": item.get("mesh_terms", []),
                    "synonyms": item.get("synonyms", []),
                    "groups": item.get("groups", []),
                    "language": item.get("language", ""),
                    "document_type": "structured_topic"
                }
            }

            f_out.write(json.dumps(unified) + "\n")

if __name__ == "__main__":
    convert()
