from rag.vector_store import search
from openai import OpenAI
from dotenv import load_dotenv
import os
import warnings

warnings.filterwarnings("ignore", module="chromadb")

load_dotenv(override=True)

client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

SYSTEM_PROMPT = """
You are HealthLens, a medical information assistant.

Rules:
- Provide educational information only.
- Do NOT diagnose.
- Do NOT suggest medications.
- Do NOT give emergency instructions.
- Encourage consulting licensed healthcare professionals.
- If user asks for diagnosis or treatment, refuse politely.
- When analyzing lab reports, explain values in simple language.
- Mention if values appear outside reference range, but do NOT diagnose.
- Do NOT say it is a "lab report" in the response. Just explain the values and what they might indicate in general terms.
- Do NOT answer questions unrelated to health or lab reports. Politely decline and steer back to medical topics.
"""

DISCLAIMER = """
⚠️ This response is for educational purposes only and is not medical advice.
Always consult a qualified healthcare professional.
"""

def generate_response(raw_report_text=None, structured_lab_data=None, user_query=None):

    if user_query:
        query_for_search = user_query
    else:
        query_for_search = raw_report_text

    results = search(query_for_search, top_k=5)
    context_chunks = results["documents"][0]
    context = "\n\n".join(context_chunks)

    lab_section = ""
    if structured_lab_data:
        lab_section = "Structured Lab Data:\n"
        for item in structured_lab_data:
            lab_section += f"{item['test_name']} = {item['value']} {item['unit']} (Ref: {item['reference_range']})\n"

    prompt = f"""
Context:
{context}

{lab_section}

User Question:
{user_query if user_query else "Please explain this medical report."}

Full OCR Report Text:
{raw_report_text if raw_report_text else ""}
"""

    response = client.chat.completions.create(
        model="gemini-3-flash-preview",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    final_answer = response.choices[0].message.content

    return final_answer + "\n\n" + DISCLAIMER


if __name__ == "__main__":
    print(generate_response(user_query="What is A1C?"))