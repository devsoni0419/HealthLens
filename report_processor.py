import os
import re
from ocr_utils import extract_text_from_image, extract_text_from_pdf
from generator import generate_response

def extract_all_lab_values(text):
    pattern = r"([A-Za-z .()%/]+?)\s+(\d+\.?\d*)\s*([A-Za-z/%]+)?\s+(\d+\.?\d*\s*[-–]\s*\d+\.?\d*)"
    matches = re.findall(pattern, text)

    results = []

    for match in matches:
        test_name = match[0].strip()
        value = match[1]
        unit = match[2] if match[2] else ""
        reference_range = match[3]

        results.append({
            "test_name": test_name,
            "value": value,
            "unit": unit,
            "reference_range": reference_range
        })

    return results


def process_report(file_path):
    ext = os.path.splitext(file_path)[1].lower()

    if ext in [".png", ".jpg", ".jpeg"]:
        text = extract_text_from_image(file_path)
    elif ext == ".pdf":
        text = extract_text_from_pdf(file_path)
    else:
        raise ValueError("Unsupported file type")

    if not text.strip():
        return "No readable text found in the report."

    lab_data = extract_all_lab_values(text)

    response = generate_response(
        raw_report_text=text,
        structured_lab_data=lab_data
    )

    return response