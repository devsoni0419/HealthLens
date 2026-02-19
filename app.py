import gradio as gr
from rag.vector_store import search
from openai import OpenAI
from dotenv import load_dotenv
import os
import warnings

warnings.filterwarnings("ignore", module="chromadb")
load_dotenv(override=True)

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
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
-If you don't know the answer, say you don't know and suggest consulting a healthcare professional.
"""

DISCLAIMER = """
⚠️ This response is for educational purposes only and is not medical advice.
Always consult a qualified healthcare professional.
"""

def generate_answer(user_query):
    results = search(user_query, top_k=5)
    context_chunks = results["documents"][0]
    context = "\n\n".join(context_chunks)

    prompt = f"""
Context:
{context}

User Question:
{user_query}
"""

    response = client.chat.completions.create(
        model="meta-llama/llama-3.3-70b-instruct:free",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    final_answer = response.choices[0].message.content
    return final_answer + "\n\n" + DISCLAIMER


def chat(message, history):
    return generate_answer(message)


app = gr.ChatInterface(
    fn=chat,
    title="🏥 HealthLens AI",
    description="Educational medical assistant (Non-diagnostic)"
)

app.launch(share=True)
