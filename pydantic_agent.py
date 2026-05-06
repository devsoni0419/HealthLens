from pydantic_ai import Agent
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv(override=True)


from tracker import save_and_message, get_history, get_insights
from reminder import set_reminder as set_reminder_func
from rag.vector_store import search
from report_processor import extract_text_from_image, extract_text_from_pdf, extract_all_lab_values

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
- Use the provided tools to extract text from a report file.
- Explain medical values in simple, easy-to-understand language.
- Clearly mention if values are low, normal, or high based on reference range.
- Do NOT diagnose conditions based on report.

TOOL USAGE:
- You have tools to track health metrics (like bp, sugar), retrieve health history, set reminders, search medical knowledge, and read report files.
- ALWAYS use `search_medical_knowledge` if the user asks a medical question and you need context.
- If a user provides a file path in their query, use `read_report_file` to analyze it.

RESPONSE STYLE:
- Keep answers simple, clear, and structured.
- Be supportive but not alarming.
- Focus on awareness, prevention, and guidance.
- ALWAYS append this disclaimer to medical responses: "⚠️ This response is for educational purposes only and is not medical advice. Always consult a qualified healthcare professional."
"""

agent = Agent(
    'gemini-3-flash-preview',
    system_prompt=SYSTEM_PROMPT
)

@agent.tool_plain
def save_health_metric(metric: str, value: float) -> str:
    """Saves a health metric like blood pressure ('bp') or blood sugar ('sugar') and its value."""
    return save_and_message(metric, value)

@agent.tool_plain
def get_health_history() -> str:
    """Retrieves the user's past logged health metrics and their status."""
    return get_history()

@agent.tool_plain
def get_health_insights() -> str:
    """Analyzes the user's health history to provide trends and averages."""
    return get_insights()

@agent.tool_plain
def set_reminder(minutes_from_now: int) -> str:
    """Sets a health reminder for the user to be notified in `minutes_from_now` minutes."""
    target = datetime.now() + timedelta(minutes=minutes_from_now)
    date_str = target.strftime("%Y-%m-%d")
    time_str = target.strftime("%H:%M")
    return set_reminder_func("Health Reminder", date_str, time_str)

@agent.tool_plain
def search_medical_knowledge(query: str) -> str:
    """Searches the trusted medical vector database for information to answer user's medical questions."""
    results = search(query, top_k=5)
    if not results or not results.get("documents") or not results["documents"][0]:
        return "No relevant medical context found in the database."
    context_chunks = results["documents"][0]
    return "\n\n".join(context_chunks)

@agent.tool_plain
def read_report_file(file_path: str) -> str:
    """Extracts raw text and structured lab values from a given medical report file (.pdf, .jpg, .png)."""
    ext = os.path.splitext(file_path)[1].lower()
    
    try:
        if ext in [".png", ".jpg", ".jpeg"]:
            text = extract_text_from_image(file_path)
        elif ext == ".pdf":
            text = extract_text_from_pdf(file_path)
        else:
            return f"Error: Unsupported file type '{ext}'."
        
        if not text.strip():
            return "No readable text found in the report."
            
        lab_data = extract_all_lab_values(text)
        
        output = f"--- RAW TEXT ---\n{text}\n\n--- STRUCTURED LAB DATA ---\n"
        for item in lab_data:
            output += f"{item['test_name']} = {item['value']} {item['unit']} (Ref: {item['reference_range']})\n"
        
        return output
    except Exception as e:
        return f"Failed to read report: {str(e)}"
