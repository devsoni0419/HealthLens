import gradio as gr
from generator import generate_response
from report_processor import process_report
from tracker import save_and_message, get_history, get_insights, plot_metric
from reminder import set_reminder
from pydantic_agent import agent
from safety import safety_wrapper
import warnings

warnings.filterwarnings("ignore", module="chromadb")


def agent_router(query, file=None):
    prompt = query
    
    if file is not None:
        prompt += f"\n\n[USER UPLOADED FILE PATH]: {file.name}\nPlease use the read_report_file tool to read and analyze this report."
        
    try:
        result = agent.run_sync(prompt)
        response = result.output
        return safety_wrapper(query, response)
    except Exception as e:
        return f"❌ Agent encountered an error: {str(e)}"


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