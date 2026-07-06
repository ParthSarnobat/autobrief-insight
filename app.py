import gradio as gr
from workflow import ScoutAgent, AnalystAgent, InterrogatorAgent

# Global state to hold the latest report context for the Interrogator
latest_context = "No analysis has been generated yet. Please click '🚀 Fetch Today's AI News' first."

def run_pipeline() -> str:
    """
    Autonomously triggers the Scout and Analyst agents to fetch and format today's AI news.
    """
    global latest_context
    
    scout = ScoutAgent()
    scraped_data = scout.run()
    
    if "Error gathering data:" in scraped_data:
        return f"## Analysis Failed\n{scraped_data}"
        
    analyst = AnalystAgent()
    analysis_html, analysis_context = analyst.run(scraped_data)
    
    # Update the shared state/memory so the Interrogator has access to it
    latest_context = analysis_context
    return analysis_html

def chat_interface_fn(message, history):
    """
    Handles chat messages for the Interrogator agent.
    The Interrogator securely sanitizes the payload natively inside its run method.
    """
    global latest_context
    interrogator = InterrogatorAgent()
    
    # Process the message against the global report context
    response = interrogator.run(message, context=latest_context)
    return response

custom_css = """
.card-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; width: 100%; height: auto !important; padding: 10px; }

.news-card { 
    background: linear-gradient(145deg, #1e293b, #0f172a); 
    border-radius: 12px; 
    padding: 24px; 
    box-shadow: 0 4px 15px rgba(0,0,0,0.4); 
    transition: all 0.3s ease; 
    min-height: 420px; /* Increased height */
    overflow: visible !important; 
    display: flex; 
    flex-direction: column; 
    justify-content: space-between;
    border-top: 4px solid #f97316; /* Orange top accent */
    border-bottom: 1px solid #334155;
    border-left: 1px solid #334155;
    border-right: 1px solid #334155;
}

.news-card:hover { 
    transform: translateY(-8px); 
    box-shadow: 0 15px 30px rgba(249, 115, 22, 0.3), inset 0 1px 2px rgba(255, 255, 255, 0.1); 
}

.news-title { 
    background: linear-gradient(90deg, #f97316, #fbbf24);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 1.2em; 
    margin-bottom: 20px; 
    font-weight: 800; 
    line-height: 1.4;
    white-space: normal !important; 
    word-wrap: break-word !important; 
}

.news-bullet { 
    color: #94a3b8; 
    margin-bottom: 12px; 
    font-size: 0.95em; 
    white-space: normal !important; 
    word-wrap: break-word !important; 
    display: block; 
    line-height: 1.6;
    border-left: 2px solid #ea580c; /* Custom modern bullet line */
    padding-left: 12px;
}

.news-bullet:hover {
    color: #e2e8f0;
}

.news-link { 
    color: #fb923c; 
    font-weight: bold; 
    text-decoration: none; 
    margin-top: 20px; 
    display: inline-block;
    padding: 8px 16px;
    background: rgba(249, 115, 22, 0.1);
    border-radius: 6px;
    text-align: center;
    transition: background 0.2s ease;
}

.news-link:hover {
    background: rgba(249, 115, 22, 0.2);
    color: #fdba74;
}

.primary-btn-class:hover {
    background: linear-gradient(135deg, rgba(251, 146, 60, 1) 0%, rgba(249, 115, 22, 0.7) 100%) !important;
    box-shadow: 0 0 15px rgba(249, 115, 22, 0.5), inset 0 1px 2px rgba(255, 255, 255, 0.4) !important;
    backdrop-filter: blur(4px);
    transform: translateY(-1px);
}

/* --- CHATBOT UI SEAMLESS POLISH --- */

/* 1. Completely hide the 'Chatbot' label/tag */
.gradio-chatbot .label-wrap,
.gradio-chatbot > div:first-child {
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
}

/* 2. Blend Chat History Container with Background */
.gradio-chatbot {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

/* Keep User bubbles (Orange Gradient) */
.message.user {
    background: linear-gradient(135deg, #ea580c, #f97316) !important;
    color: #ffffff !important;
    border-radius: 12px 12px 0 12px !important;
    border: none !important;
    box-shadow: 0 4px 10px rgba(249, 115, 22, 0.2) !important;
}

/* Keep Bot bubbles (Dark with orange accent) */
.message.bot {
    background: #0f172a !important;
    color: #e2e8f0 !important;
    border: 1px solid #334155 !important;
    border-left: 3px solid #ea580c !important; 
    border-radius: 12px 12px 12px 0 !important;
    box-shadow: 0 4px 6px rgba(0,0,0,0.3) !important;
    line-height: 1.6 !important;
}

/* 3. Destroy the Nested 3-Container Look */
/* This strips the background and borders from all of Gradio's outer wrapper layers */
.gradio-container .form,
.gradio-container .block,
.gradio-container .wrap,
.gradio-container label.textarea {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

/* 4. Style the ACTUAL text box as the single, visible container */
.gradio-container textarea {
    background: #1e293b !important; /* Matches the dark cards */
    border: 1px solid #334155 !important;
    border-radius: 24px !important; /* Nice pill-shaped modern look */
    padding: 14px 20px !important;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3) !important;
    color: #f8fafc !important;
    transition: all 0.3s ease !important;
}

/* 5. Glowing Orange Border when Typing (Focus State) */
.gradio-container textarea:focus {
    border-color: #f97316 !important;
    box-shadow: 0 0 0 1px #f97316, 0 0 20px rgba(249, 115, 22, 0.4) !important;
    outline: none !important;
}

/* 6. Clean up the Submit/Send Arrow Button */
.gradio-container button[aria-label="Submit"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: #f97316 !important;
    transition: all 0.2s ease !important;
}
.gradio-container button[aria-label="Submit"]:hover {
    transform: scale(1.1) !important;
    color: #fbbf24 !important;
}
"""

# Apply the theme and CSS
with gr.Blocks(theme=gr.themes.Soft(primary_hue="orange"), css=custom_css, title="AI News Agent Dashboard") as demo:
    # Inject the SVG directly into the UI
    gr.HTML("""
        <div style="display: flex; justify-content: center; padding: 20px 0;">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 520 120" width="350" height="80">
                <defs>
                    <linearGradient id="brandGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stop-color="#f97316" /><stop offset="100%" stop-color="#fbbf24" />
                    </linearGradient>
                </defs>
                <g transform="translate(10, 20)">
                    <path d="M 40 5 L 75 25 L 75 65 L 40 85 L 5 65 L 5 25 Z" fill="none" stroke="url(#brandGradient)" stroke-width="4"/>
                    <path d="M 40 25 L 58 35 L 58 55 L 40 65 L 22 55 L 22 35 Z" fill="url(#brandGradient)" opacity="0.8"/>
                    <circle cx="40" cy="45" r="6" fill="#0f172a" />
                </g>
                <text x="110" y="72" font-family="system-ui, sans-serif" font-size="42" font-weight="800" fill="#f8fafc" letter-spacing="-1">Autobrief</text>
                <text x="315" y="72" font-family="system-ui, sans-serif" font-size="42" font-weight="300" fill="url(#brandGradient)">Insight</text>
            </svg>
        </div>
    """)
    gr.Markdown("<div style='text-align: center; color: #94a3b8;'>Your daily AI briefing, curated and interrogated</div>")
    
    with gr.Tabs():
        # Tab 1: Daily Insight Engine
        with gr.Tab("Daily Insight Engine"):
            gr.Markdown("Click the button below to deploy the **Scout** and **Analyst** agents. They will autonomously fetch today's AI news and compile a structured Markdown report.")
            
            with gr.Row():
                gr.Column(scale=1)  # Left spacer
                with gr.Column(scale=1, min_width=250):
                    trigger_btn = gr.Button("🚀 Fetch Today's AI News", variant="primary", elem_classes=["primary-btn-class"])
                gr.Column(scale=1)  # Right spacer
                
            report_output = gr.HTML(label="Compiled Daily Report", value="<div style='color:#94a3b8; font-style:italic;'>The report will appear here once generated.</div>")
            
            trigger_btn.click(
                fn=run_pipeline,
                inputs=[],
                outputs=[report_output]
            )
            
        # Tab 2: Interrogator Terminal
        with gr.Tab("Interrogator Terminal"):
            gr.Markdown("Ask follow-up questions about the generated report. The **Interrogator** agent securely sanitizes all inputs and uses the generated report as context.")
            
            chat = gr.ChatInterface(
                fn=chat_interface_fn,
                chatbot=gr.Chatbot(show_label=False)
            )

if __name__ == "__main__":
    # Launch on a specific port
    demo.launch(server_name="127.0.0.1", server_port=7860)
