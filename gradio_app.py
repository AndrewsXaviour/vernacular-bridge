import gradio as gr
import os
import time
import json
from dotenv import load_dotenv
from orchestrator import generate_content
from models.request import QueryRequest

# Load environment variables
load_dotenv()

# --- CUSTOM CSS ---
CSS = """
.container { padding: 20px; max-width: 1400px; margin: auto; }
.card { 
    padding: 24px; 
    border-radius: 16px; 
    margin-bottom: 20px; 
    border: 1px solid #e2e8f0; 
    background: white;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    transition: transform 0.2s;
}
.card:hover { transform: translateY(-2px); }
.tamil-card { border-left: 6px solid #4f46e5; background-color: #f8faff; }
.english-card { border-left: 6px solid #f59e0b; background-color: #fffcf5; }
.step-card { border-left: 6px solid #10b981; background-color: #f0fdf4; }
.decoder-card { border-left: 6px solid #ec4899; background-color: #fdf2f8; }
.label { font-weight: 700; color: #1e293b; margin-bottom: 8px; display: block; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.05em; }
.content { color: #334155; line-height: 1.6; font-size: 1.1rem; }
.step-item { padding: 8px 0; border-bottom: 1px soft #e2e8f0; display: flex; align-items: flex-start; }
.step-num { background: #10b981; color: white; border-radius: 50%; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center; margin-right: 12px; flex-shrink: 0; font-size: 0.8rem; margin-top: 2px; }
.error-box { background-color: #fef2f2; border: 1px solid #fee2e2; border-radius: 12px; padding: 20px; color: #991b1b; text-align: center; }
.status-msg { font-style: italic; color: #6366f1; font-weight: 600; text-align: center; margin-top: 10px; }
"""

def format_card(label, content, card_class=""):
    return f"""
    <div class="card {card_class}">
        <span class="label">{label}</span>
        <div class="content">{content}</div>
    </div>
    """

def format_steps(steps):
    items = "".join([f'<div class="step-item"><span class="step-num">{i+1}</span><div class="content">{step}</div></div>' for i, step in enumerate(steps)])
    return f"""
    <div class="card step-card">
        <span class="label">📘 Step-by-step clarity</span>
        {items}
    </div>
    """

def format_decoder(qd):
    return f"""
    <div class="card decoder-card">
        <span class="label">🎯 Question Decoder</span>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
            <div><span class="label" style="font-size: 0.7rem;">Type</span><div class="content" style="font-weight: 600; color: #ec4899;">{qd.question_type.upper()}</div></div>
            <div><span class="label" style="font-size: 0.7rem;">Goal</span><div class="content" style="font-size: 0.95rem;">{qd.expected_structure}</div></div>
        </div>
        <div style="margin-top: 15px;">
            <span class="label" style="font-size: 0.7rem;">Answer Template</span>
            <div class="content" style="background: #fff; padding: 10px; border-radius: 8px; border: 1px dashed #ec4899; font-size: 0.9rem; font-family: monospace;">{qd.answer_template}</div>
        </div>
    </div>
    """

def process_input(user_input):
    if not user_input or len(user_input) < 3:
        yield {
            status_box: gr.update(value="Please enter a valid concept (min 3 chars)", visible=True),
            main_container: gr.update(visible=False),
            error_container: gr.update(visible=False)
        }
        return

    # Phase 1: Analyzing
    yield {
        status_box: gr.update(value="🔍 Analyzing concept...", visible=True),
        main_container: gr.update(visible=False),
        right_panel: gr.update(visible=False),
        error_container: gr.update(visible=False),
        submit_btn: gr.update(interactive=False)
    }
    time.sleep(0.8)

    # Phase 2: Generating
    yield {
        status_box: gr.update(value="🧠 Generating explanation..."),
    }
    
    # CALL BACKEND
    try:
        request = QueryRequest(user_input=user_input)
        response = generate_content(request)
        
        if response.get("status") != "success":
            raise ValueError(response.get("message", "Unknown error"))
            
        data = response.get("data")
        
        # Phase 3: Preparing Questions
        yield {
            status_box: gr.update(value="🎓 Preparing exam questions..."),
        }
        time.sleep(0.5)

        # Build Output Components
        tamil_html = format_card("🧠 Understand in your language", data.tamil_simple, "tamil-card")
        english_html = format_card("🎓 Write in exam language", data.english_academic, "english-card")
        steps_html = format_steps(data.steps)
        decoder_html = format_decoder(data.question_decoder)

        # MCQ Logic
        mcq_updates = []
        for i in range(5):
            if i < len(data.mcqs):
                m = data.mcqs[i]
                # Filter out the 'raw answer' suffix if present in options (as seen in trace)
                clean_options = [opt for opt in m.options if opt != m.correct_answer]
                if len(clean_options) < 4:
                     # If we removed the answer, it was likely already there or we need to keep it.
                     # Actually, the trace showed [A), B), C), D), C]. 
                     # Let's just take first 4.
                     clean_options = m.options[:4]
                
                # Store correct answer in a hidden state for comparison
                mcq_updates.append(gr.update(label=f"Question {i+1}: {m.question}", choices=clean_options, value=None, visible=True))
                mcq_updates.append(m.correct_answer) # Correct answer for state
            else:
                mcq_updates.append(gr.update(visible=False))
                mcq_updates.append("")

        yield {
            status_box: gr.update(visible=False),
            main_container: gr.update(visible=True),
            right_panel: gr.update(visible=True),
            error_container: gr.update(visible=False),
            submit_btn: gr.update(interactive=True),
            tamil_out: tamil_html,
            english_out: english_html,
            steps_out: steps_html,
            decoder_out: decoder_html,
            # MCQs
            mcq1_box: mcq_updates[0], mcq1_ans: mcq_updates[1],
            mcq2_box: mcq_updates[2], mcq2_ans: mcq_updates[3],
            mcq3_box: mcq_updates[4], mcq3_ans: mcq_updates[5],
            mcq4_box: mcq_updates[6], mcq4_ans: mcq_updates[7],
            mcq5_box: mcq_updates[8], mcq5_ans: mcq_updates[9],
            mcq1_feedback: "", mcq2_feedback: "", mcq3_feedback: "", mcq4_feedback: "", mcq5_feedback: ""
        }

    except Exception as e:
        yield {
            status_box: gr.update(visible=False),
            main_container: gr.update(visible=False),
            right_panel: gr.update(visible=False),
            error_container: gr.update(visible=True),
            error_msg: f"Error: {str(e)}",
            submit_btn: gr.update(interactive=True)
        }

def check_mcq(user_choice, correct_answer):
    if not user_choice: return ""
    # Check if the choice starts with the correct answer letter (e.g. "A)" vs "A")
    if user_choice.startswith(correct_answer) or correct_answer in user_choice:
        return "✅ Correct!"
    return f"❌ Incorrect. The correct answer is {correct_answer}."

with gr.Blocks(title="Vernacular Bridge") as demo:
    gr.HTML("<h1 style='text-align: center; color: #1e293b; margin-top: 20px;'>🌉 Vernacular Bridge</h1>")
    gr.HTML("<p style='text-align: center; color: #64748b;'>Bridging the gap between conceptual understanding and academic expression</p>")
    
    with gr.Row(elem_classes="container"):
        # --- LEFT PANEL: INPUT ---
        with gr.Column(scale=1):
            with gr.Group():
                input_box = gr.Textbox(
                    label="What concept do you want to master?", 
                    placeholder="Enter in Tamil or English (e.g., Photosynthesis)",
                    lines=3
                )
                submit_btn = gr.Button("🚀 Transform Concept", variant="primary")
                retry_btn = gr.Button("🔄 Retry", visible=False)
            
            status_box = gr.Markdown("", visible=False, elem_classes="status-msg")
            
            error_container = gr.Column(visible=False)
            with error_container:
                error_msg = gr.HTML(elem_classes="error-box")
                retry_btn_error = gr.Button("Retry")

        # --- CENTER PANEL: LEARNING TRANSFORMATION ---
        with gr.Column(scale=2, visible=False) as main_container:
            tamil_out = gr.HTML()
            english_out = gr.HTML()
            steps_out = gr.HTML()

        # --- RIGHT PANEL: EXAM INTELLIGENCE ---
        with gr.Column(scale=2, visible=False) as right_panel:
            decoder_out = gr.HTML()
            
            with gr.Group():
                gr.HTML("<span class='label' style='margin-top: 20px;'>📝 Quick Assessment</span>")
                
                # Question 1
                mcq1_box = gr.Radio(label="Question 1", visible=False)
                mcq1_ans = gr.State("")
                mcq1_feedback = gr.Markdown("")
                
                # Question 2
                mcq2_box = gr.Radio(label="Question 2", visible=False)
                mcq2_ans = gr.State("")
                mcq2_feedback = gr.Markdown("")
                
                # Question 3
                mcq3_box = gr.Radio(label="Question 3", visible=False)
                mcq3_ans = gr.State("")
                mcq3_feedback = gr.Markdown("")
                
                # Question 4
                mcq4_box = gr.Radio(label="Question 4", visible=False)
                mcq4_ans = gr.State("")
                mcq4_feedback = gr.Markdown("")
                
                # Question 5
                mcq5_box = gr.Radio(label="Question 5", visible=False)
                mcq5_ans = gr.State("")
                mcq5_feedback = gr.Markdown("")

    # Event Handlers
    submit_btn.click(
        process_input, 
        inputs=[input_box], 
        outputs=[
            status_box, main_container, error_container, submit_btn,
            tamil_out, english_out, steps_out, decoder_out,
            mcq1_box, mcq1_ans, mcq2_box, mcq2_ans, mcq3_box, mcq3_ans, mcq4_box, mcq4_ans, mcq5_box, mcq5_ans,
            mcq1_feedback, mcq2_feedback, mcq3_feedback, mcq4_feedback, mcq5_feedback,
            error_msg,
            right_panel # Add right_panel to outputs
        ]
    )
    
    retry_btn_error.click(
        process_input, 
        inputs=[input_box], 
        outputs=[
            status_box, main_container, error_container, submit_btn,
            tamil_out, english_out, steps_out, decoder_out,
            mcq1_box, mcq1_ans, mcq2_box, mcq2_ans, mcq3_box, mcq3_ans, mcq4_box, mcq4_ans, mcq5_box, mcq5_ans,
            mcq1_feedback, mcq2_feedback, mcq3_feedback, mcq4_feedback, mcq5_feedback,
            error_msg,
            right_panel
        ]
    )

    # MCQ Feedback Handlers
    mcq1_box.change(check_mcq, inputs=[mcq1_box, mcq1_ans], outputs=[mcq1_feedback])
    mcq2_box.change(check_mcq, inputs=[mcq2_box, mcq2_ans], outputs=[mcq2_feedback])
    mcq3_box.change(check_mcq, inputs=[mcq3_box, mcq3_ans], outputs=[mcq3_feedback])
    mcq4_box.change(check_mcq, inputs=[mcq4_box, mcq4_ans], outputs=[mcq4_feedback])
    mcq5_box.change(check_mcq, inputs=[mcq5_box, mcq5_ans], outputs=[mcq5_feedback])

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, css=CSS)
