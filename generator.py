from rag.vector_store import search
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
import os
import warnings

warnings.filterwarnings("ignore", module="chromadb")

load_dotenv(override=True)

client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

SYSTEM_PROMPT = """
You are HealthLens, a non-diagnostic medical information assistant.

CORE RULES:
- Provide educational information only.
- Do NOT diagnose any condition.
- Do NOT prescribe or suggest medications or dosages.
- Do NOT replace a licensed healthcare professional.
- Encourage users to consult a doctor for medical concerns.
- Do NOT answer non-health-related questions.

SAFETY (CRITICAL):
- If user mentions symptoms like chest pain, difficulty breathing, severe bleeding, unconsciousness, stroke signs, seizures, suicide thoughts, or overdose:
  → Clearly state this may be a medical emergency.
  → Strongly advise seeking immediate medical help or emergency services.
  → Do NOT provide treatment steps.

LAB REPORT ANALYSIS:
- Explain medical values in simple, easy-to-understand language.
- Clearly mention if values are low, normal, or high based on reference range.
- Do NOT diagnose conditions based on report.

RESPONSE STYLE:
- Keep answers simple, clear, and structured.
- Be supportive but not alarming.
- Focus on awareness, prevention, and guidance.

REFUSAL RULE:
- If asked for diagnosis, prescriptions, or treatment plans:
  → Politely refuse and redirect to a healthcare professional.
"""

DISCLAIMER = """
⚠️ This response is for educational purposes only and is not medical advice.
Always consult a qualified healthcare professional.
"""


def check_emergency(query):
    emergency_keywords = [
        "chest pain", "difficulty breathing", "shortness of breath",
        "unconscious", "seizure", "heart attack", "stroke",
        "severe bleeding", "high fever", "suicidal",
        "fainting", "collapse", "not breathing"
    ]

    query = query.lower()

    for word in emergency_keywords:
        if word in query:
            return True
    return False


def generate_response(raw_report_text=None, structured_lab_data=None, user_query=None):

    # 🚨 Emergency check
    if user_query and check_emergency(user_query):
        return "🚨 This may be a medical emergency. Please seek immediate medical attention or call your local emergency number.\n\n" + DISCLAIMER

    # 🕒 Inject current time
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M")

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

    # 🧠 Updated prompt with time
    prompt = f"""
Current DateTime: {current_time}

Context:
{context}

{lab_section}

User Question:
{user_query if user_query else "Explain this medical report"}

Report Text:
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