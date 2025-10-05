import streamlit as st
from utils import call_search, call_generate, call_validate, call_design
import json
import time
import pandas as pd
from pathlib import Path

st.set_page_config(
    page_title="Neuro Agent: Alzheimer’s Research Pipeline",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.html("""
<style>
    /* Global dark theme */
    .stApp {
        background: #0f0c14;
        color: #ecf0f1;
    }
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background: #1a1a2e;
        color: #ecf0f1;
        padding: 20px;
        border-radius: 0 10px 10px 0;
    }
    .sidebar .sidebar-content h2 {
        color: #3498db;
        font-size: 1.8rem;
        text-align: center;
        margin-bottom: 20px;
    }
    .sidebar .stTextInput, .sidebar .stNumberInput, .sidebar .stCheckbox {
        background: #2e2e3e;
        border-radius: 8px;
        padding: 5px;
        margin-bottom: 15px;
    }
    .sidebar .stTextInput > div > div > input, .sidebar .stNumberInput > div > div > input {
        background: #2e2e3e;
        color: #ecf0f1;
        border: 1px solid #3498db;
        border-radius: 5px;
    }
    .sidebar .stButton > button {
        background: linear-gradient(45deg, #3498db, #8e44ad);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
        width: 100%;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .sidebar .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 5px 15px rgba(52, 152, 219, 0.5);
    }
    /* Main content card */
    .main-card {
        background: #1e1e2f;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        color: #ecf0f1;
        margin-bottom: 20px;
        border-left: 4px solid #3498db;
        transition: transform 0.2s ease;
    }
    .main-card:hover {
        transform: translateY(-5px);
    }
    .header {
        font-size: 2.5rem;
        color: #ecf0f1;
        text-align: center;
        font-weight: 700;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
        margin-bottom: 10px;
    }
    .subheader {
        font-size: 1.5rem;
        color: #bdc3c7;
        text-align: center;
        font-weight: 500;
        margin-bottom: 20px;
    }
    .metric-card {
        background: #34495e;
        padding: 10px;
        border-radius: 8px;
        text-align: center;
        color: #ecf0f1;
        margin: 10px 0;
    }
    .stProgress .st-bo {
        background-color: #34495e;
    }
    .stProgress .st-bo div {
        background: linear-gradient(90deg, #3498db, #8e44ad);
    }
    .stExpander {
        background: #2e2e3e;
        border: 1px solid #3498db;
        border-radius: 8px;
    }
    .stExpander > div > div {
        color: #ecf0f1;
    }
    .stDownloadButton > button {
        background: #27ae60;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        transition: transform 0.3s ease;
    }
    .stDownloadButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 5px 15px rgba(39, 174, 96, 0.5);
    }
    /* Help icon styling */
    .help-icon {
        color: #95a5a6;
        cursor: pointer;
        font-size: 0.9rem;
        margin-left: 5px;
    }
    .help-icon:hover {
        color: #3498db;
    }
    /* Top right status */
    .status-bar {
        position: fixed;
        top: 10px;
        right: 20px;
        background: rgba(255,255,255,0.1);
        padding: 5px 10px;
        border-radius: 15px;
        font-size: 0.8rem;
        color: #ecf0f1;
        z-index: 999;
    }
    /* Ensure text visibility */
    .stMarkdown p, .stMarkdown li, .stMarkdown strong {
        color: #ecf0f1 !important;
    }
</style>
""")

st.html("<div class='status-bar'>🔗 CONNECTING</div>")

with st.sidebar:
    st.html("<h2>💬 Pipeline Controls</h2>")
    st.html("<p class='main-card'>Configure and launch the CerebroDiscover pipeline.</p>")

    query = st.text_input(
        "Research Question",
        value="Why do anti-amyloid drugs fail?",
        placeholder="e.g., Role of tau in Alzheimer's",
        help="Enter a specific question about Alzheimer’s disease."
    )

    top_k = st.number_input(
        "Top-k Papers",
        min_value=1,
        max_value=10,
        value=3,
        help="Number of papers to retrieve (1-10)."
    )

    show_metrics = st.checkbox(
        "Show Performance Metrics",
        value=True,
        help="Display latency for each pipeline step."
    )

    show_raw_json = st.checkbox(
        "Show Raw JSON Outputs",
        value=False,
        help="Show raw API responses for debugging."
    )

    run = st.button("🚀 Run Discovery Pipeline")

st.html("<h1 class='header'>Neuro-Symbolic Research Scientist Agent for Alzheimer’s Disease 🧠</h1>")
st.html("<p class='subheader'>Unraveling Alzheimer’s Disease with AI</p>")

st.html("""
<div class='main-card'>
    <p><strong style="color:#60a5fa;">Neuro-Symbolic Research Scientist</strong> is an advanced research assistant designed to accelerate discovery in Alzheimer’s disease. 
    By combining intelligent literature retrieval, hypothesis generation, logical validation, and experiment design, it simulates the reasoning workflow of a human neuroscientist — bridging AI and biology seamlessly.</p>

    <h3 style="color:#93c5fd;">How It Works</h3>
    <ul style="line-height:1.8;">
        <li><strong>🔵 Ingest & Search (Port 8000)</strong>: Searches a curated Pinecone-based vector database of Alzheimer’s literature.</li>
        <li><strong>🤖 Hypothesis Generation (Port 8001)</strong>: Reads the retrieved literature and formulates testable hypotheses.</li>
        <li><strong>✅ Logical Validation (Port 8002)</strong>: Uses a Z3 theorem prover to check the hypothesis for logical consistency.</li>
        <li><strong>🧪 Experiment Design (Port 8003)</strong>: If validated, generates a complete experimental blueprint for lab testing.</li>
    </ul>

    <h3 style="color:#93c5fd;">Hackathon Vision</h3>
    <p>Built for the <strong>FutureStack GenAI Hackathon 2025</strong>, 
    <strong>Neuro-Scientist</strong> bridges AI and neuroscience to tackle Alzheimer’s disease.</p>

    <p><strong>Team</strong>: CoreV2 | <em>Built with ❤️ by Vicky Gupta & Vaibhav Adhikari</em><br>
    <strong>Tech Stack</strong>: Python, FastAPI, Z3, Pinecone, Cerebras LLaMA3.1-8B, Streamlit, Docker<br>
    <strong>Contact</strong>: 
    <a href="mailto:vickyguptagkp55@gmail.com" style="color: #60a5fa;">neuroai</a></p>
</div>
""")

if run:
    progress = st.progress(0)
    st.html("<h2 class='subheader'>Pipeline Results</h2>")
    
    # Step 1: Search
    try:
        with st.spinner("🔍 Searching papers..."):
            res = call_search(query, top_k=top_k)
            papers = res["response"].get("papers", [])
            progress.progress(25)
            st.subheader("📄 Papers Retrieved")
            for p in papers:
                st.html(f"""
                <div class='main-card'>
                    <strong>Title</strong>: {p.get('title', 'N/A')} (ID: {p.get('id', 'N/A')})<br>
                    <strong>Abstract</strong>: {p.get('abstract', 'N/A')[:300] + '...' if len(p.get('abstract', '')) > 300 else p.get('abstract', 'N/A')}
                </div>
                """)
            if show_metrics:
                st.html(f"<div class='metric-card'>Search Latency: {res['latency']:.2f} s</div>")
            if show_raw_json:
                with st.expander("Raw Search Output"):
                    st.json(res["response"])
    except Exception as e:
        st.error(f"Search failed: {str(e)}")
        st.stop()

    # Step 2: Generate Hypothesis
    try:
        with st.spinner("🤖 Generating hypothesis..."):
            hyp = call_generate(papers, query)["response"]
            progress.progress(50)
            st.subheader("🧪 Generated Hypothesis")
            st.html(f"""
            <div class='main-card'>
                <strong>Gap</strong>: {hyp.get('gap', 'N/A')}<br>
                <strong>Hypothesis</strong>: {hyp.get('hypothesis', 'N/A')}<br>
                <strong>Prediction</strong>: {hyp.get('prediction', 'N/A')}
            </div>
            """)
            st.html("<strong>Evidence</strong>")
            for e in hyp.get("evidence", []):
                st.html(f"<div class='main-card'><p>🔹 {e or 'No evidence'}</p></div>")
            st.html("<strong>Logical Rules</strong>")
            rules_df = pd.DataFrame(hyp.get("rules", []), columns=["Rule"])
            st.html(f"<div class='main-card'>{rules_df.to_html(index=False) if not rules_df.empty else '<p>No rules generated</p>'}</div>")
            st.html(f"<div class='main-card'><strong>Classification</strong>: {hyp.get('classification', 'Unknown')}</div>")
            st.html(f"<div class='main-card'><strong>Further Insights</strong>: {hyp.get('further_data', 'None')}</div>")
            if show_metrics:
                st.html(f"<div class='metric-card'>Hypothesis Generation Latency: {call_generate(papers, query)['latency']:.2f} s</div>")
            if show_raw_json:
                with st.expander("Raw Hypothesis Output"):
                    st.json(hyp)
    except Exception as e:
        st.error(f"Hypothesis generation failed: {str(e)}")
        st.stop()

    # Step 3: Validate
    validation_result = None
    try:
        with st.spinner("✔️ Validating hypothesis with Z3..."):
            hyp_input = {
                "gap": hyp.get("gap", ""),
                "hypothesis": hyp.get("hypothesis", ""),
                "evidence": hyp.get("evidence", []),
                "prediction": hyp.get("prediction", ""),
                "rules": hyp.get("rules", []),
                "classification": hyp.get("classification", ""),
                "further_data": hyp.get("further_data", "")
            }
            val = call_validate(hyp_input)
            validation_result = val["response"].get("validation_result", {}).get("additionalProp1", {})
            progress.progress(75)
            st.subheader("✅ Validation Result")
            if validation_result.get("valid"):
                st.success("✅ Hypothesis is VALID")
            else:
                st.error("❌ Hypothesis is INVALID")
            st.html(f"<div class='main-card'><strong>Reason</strong>: {validation_result.get('reason', 'N/A')}</div>")
            st.html("<strong>Proof Trace</strong>")
            for step in validation_result.get("proof_trace", []):
                st.html(f"<div class='main-card'><p>🔹 {step or 'No step'}</p></div>")
            if validation_result.get("warnings"):
                st.warning("**Warnings**: " + "; ".join(validation_result.get("warnings", [])))
            if show_metrics:
                st.html(f"<div class='metric-card'>Validation Latency: {val['latency']:.2f} s</div>")
            if show_raw_json:
                with st.expander("Raw Validation Output"):
                    st.json(val["response"])
    except Exception as e:
        st.error(f"Validation failed: {str(e)}")
        st.warning("Validation error occurred, proceeding with available data if possible.")
        validation_result = {"valid": False, "reason": f"Validation failed due to: {str(e)}", "proof_trace": ["Validation error"], "warnings": []}

    # Step 4: Design Experiment
    if validation_result and validation_result.get("valid"):
        try:
            with st.spinner("🧬 Designing experiment..."):
                design_input = {
                    "gap": hyp.get("gap", ""),
                    "hypothesis": hyp.get("hypothesis", ""),
                    "evidence": hyp.get("evidence", []),
                    "prediction": hyp.get("prediction", ""),
                    "validation_result": validation_result,
                    "rules": hyp.get("rules", []),
                    "classification": hyp.get("classification", ""),
                    "further_data": hyp.get("further_data", "")
                }
                result = call_design(design_input)
                exp = result["response"]
                progress.progress(100)
                st.subheader("🧪 Experiment Blueprint")
                st.html(f"""
                <div class='main-card'>
                    <strong>Model</strong>: {exp.get('model', 'N/A')}<br>
                    <strong>Groups</strong>: {', '.join(exp.get('groups', []))}<br>
                    <strong>Sample Size per Group</strong>: {exp.get('n_per_group', 'N/A')}<br>
                    <strong>Duration</strong>: {exp.get('duration_weeks', 'N/A')} weeks<br>
                    <strong>Treatment Route</strong>: {exp.get('treatment_route', 'N/A')}<br>
                    <strong>Outcome Measures</strong>: {', '.join(exp.get('outcome_measures', []))}<br>
                    <strong>Expected Result</strong>: {exp.get('expected_result', 'N/A')}
                </div>
                """)
                st.download_button(
                    label="📥 Download Experiment JSON",
                    data=json.dumps(exp, indent=2),
                    file_name="experiment.json",
                    mime="application/json"
                )
                if exp.get("latex"):
                    st.download_button(
                        label="📜 Download LaTeX (.tex)",
                        data=exp.get("latex"),
                        file_name="experiment.tex",
                        mime="text/plain"
                    )
                if show_metrics:
                    st.html(f"<div class='metric-card'>Experiment Design Latency: {result['latency']:.2f} s</div>")
                if show_raw_json:
                    with st.expander("Raw Experiment Design Output"):
                        st.json(exp)
        except Exception as e:
            st.error(f"Experiment design failed: {str(e)}")
            st.json(design_input)
    else:
        st.info("Experiment design skipped because hypothesis is invalid or validation failed.")