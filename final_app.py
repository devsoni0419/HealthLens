import gradio as gr
from generator import generate_response
from report_processor import process_report
from tracker import save_and_message, get_history, get_insights, plot_metric
from reminder import set_reminder
from safety import safety_wrapper
from datetime import datetime, timedelta
import re
import warnings

warnings.filterwarnings("ignore", module="chromadb")


def agent_router(query, file=None):
    q = query.lower()

    if file is not None:
        return process_report(file.name)

    if "save" in q or "track" in q:
        try:
            parts = q.split()
            metric = parts[-2]
            value = parts[-1]
            return save_and_message(metric, value)
        except:
            return "❌ Format: 'save bp 120'"

    if "history" in q:
        return get_history() + "\n\n👉 To see graph, go to 'Graph' tab."

    if "insight" in q:
        return get_insights() + "\n\n👉 For visual trends, check 'Graph' tab."
    if "remind" in q:
        try:
            match = re.search(r'(\d+)\s*minute', q)
            if match:
                mins = int(match.group(1))
                target = datetime.now() + timedelta(minutes=mins)
            else:
                target = datetime.now() + timedelta(minutes=1)

            return set_reminder(
                "Health Reminder",
                target.strftime("%Y-%m-%d"),
                target.strftime("%H:%M")
            )
        except:
            return "❌ Couldn't understand reminder time"

    response = generate_response(user_query=query)
    return safety_wrapper(query, response)


def chat(message, history, file):
    return agent_router(message, file)


with gr.Blocks() as app:

    gr.Markdown("""
# 🏥 HealthLens AI (Agent Mode)
⚠️ Educational only. Not medical advice.
""")
    with gr.Tab("ℹ️ Instructions"):
        gr.Markdown("""
    ### 🧠 How to Use HealthLens Agent

    #### 💬 Chat Commands
    - Save health data:
    → `save bp 120`
    → `track sugar 140`

    - View history:
    → `show history`

    - Get insights:
    → `show insights`

    - Set reminder:
    → `remind me in 5 minutes`

    #### 📄 Report Analysis
    - Upload a report in chat → agent will analyze automatically

    #### 📈 Graphs
    - Go to **Graph tab** to see trends

    ---

    ⚠️ Educational use only. Not medical advice.
    """)
    with gr.Tab("🤖 Agent"):
        gr.Markdown("Ask Anything, Upload Report, Track Health, or Set Reminder")
        

        gr.ChatInterface(
            fn=chat,
            additional_inputs=[
                gr.File(label="Upload Report (optional)")
            ]
        )

    with gr.Tab("📈 Graph"):
        metric_select = gr.Dropdown(["bp", "sugar"], label="Select Metric")
        graph_btn = gr.Button("Show Graph")
        plot_output = gr.Plot()

        graph_btn.click(plot_metric, inputs=metric_select, outputs=plot_output)


app.launch()