import json
from pathlib import Path
from pypdf import PdfReader

RAW_PDF_FOLDER = "data"
OUTPUT_FILE = "data/processed/unified_docs.jsonl"

def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        if page.extract_text():
            text += page.extract_text() + "\n"
    return text.strip()

def process_pdfs():
    Path("data/processed").mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "a", encoding="utf-8") as f_out:
        for pdf_file in Path(RAW_PDF_FOLDER).glob("*.pdf"):
            content = extract_text_from_pdf(pdf_file)

            unified = {
                "doc_id": pdf_file.stem,
                "source": "Local PDF",
                "title": pdf_file.stem,
                "content": content,
                "metadata": {
                    "document_type": "medical_textbook",
                    "language": "English"
                }
            }

            f_out.write(json.dumps(unified) + "\n")

if __name__ == "__main__":
    process_pdfs()
