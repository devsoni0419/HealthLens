import re

def parse_lab_report(text):
    lines = text.split("\n")
    results = []

    pattern = re.compile(
        r"([A-Za-z\s]+)\s+([\d\.]+)\s*([a-zA-Z/%]+)?\s+([\d\.]+\s*-\s*[\d\.]+)"
    )

    for line in lines:
        match = pattern.search(line)
        if match:
            test_name = match.group(1).strip()
            value = match.group(2).strip()
            unit = match.group(3) if match.group(3) else ""
            reference_range = match.group(4).strip()

            results.append({
                "test_name": test_name,
                "value": value,
                "unit": unit,
                "reference_range": reference_range
            })

    return results