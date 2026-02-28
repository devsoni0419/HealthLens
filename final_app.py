import gradio as gr
from report_processor import process_report
from generator import generate_response
from rag.vector_store import search
from dotenv import load_dotenv
import os
import warnings

warnings.filterwarnings("ignore", module="chromadb")
load_dotenv(override=True)


SYSTEM_DESCRIPTION = """
🏥 HealthLens AI

• Educational medical assistant
• Upload lab reports (PDF/Image)
• Non-diagnostic explanations only
"""


def chat(message, history):
    return generate_response(user_query=message)


def analyze_report(file):
    if file is None:
        return "Please upload a report."

    result = process_report(file.name)
    return result


with gr.Blocks() as app:

    gr.Markdown("# 🏥 HealthLens AI")
    gr.Markdown("Educational Medical Assistant (Non-Diagnostic)")

    with gr.Tab("💬 Ask Question"):
        chatbot = gr.ChatInterface(
            fn=chat,
            title="Health Q&A"
        )

    with gr.Tab("📄 Analyze Report"):
        file_input = gr.File(
            label="Upload Lab Report (PDF or Image)",
            file_types=[".pdf", ".png", ".jpg", ".jpeg"]
        )
        output = gr.Markdown()

        analyze_btn = gr.Button("Analyze Report")
        analyze_btn.click(
            fn=analyze_report,
            inputs=file_input,
            outputs=output
        )

app.launch(share=True)