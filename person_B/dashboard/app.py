# # person_b/dashboard/app.py
# import streamlit as st
# from utils import call_search, call_generate, call_validate, call_design
# import json
# import time

# st.set_page_config(page_title="CerebroDiscover Dashboard", layout="wide")

# st.title("CerebroDiscover — Neuro-Symbolic Research Scientist (Alzheimer's)")

# with st.sidebar:
#     st.header("Pipeline Controls")
#     query = st.text_input("Research question", value="Why do anti-amyloid drugs fail?")
#     top_k = st.number_input("Top-k papers", min_value=1, max_value=10, value=3)
#     run = st.button("Run Discovery Pipeline")

# if run:
#     st.info("Running pipeline...")
#     # Step 1: Search
#     try:
#         with st.spinner("Searching papers..."):
#             res = call_search(query, top_k=top_k)
#             papers = res.get("papers", [])
#             st.subheader("Papers retrieved")
#             for p in papers:
#                 st.markdown(f"**{p.get('title')}** (id: {p.get('id')})")
#                 st.write(p.get("abstract")[:500] + "...")
#     except Exception as e:
#         st.error(f"Search failed: {e}")
#         st.stop()

#     # Step 2: Generate Hypothesis
#     try:
#         with st.spinner("Generating hypothesis..."):
#             hyp = call_generate(papers)
#             st.subheader("Generated Hypothesis")
#             st.json(hyp)
#     except Exception as e:
#         st.error(f"Hypothesis generation failed: {e}")
#         st.stop()

#     # Step 3: Validate
#     try:
#         with st.spinner("Validating hypothesis (Z3)..."):
#             hyp_input = {
#                 "gap": hyp.get("gap", ""),
#                 "hypothesis": hyp.get("hypothesis", ""),
#                 "evidence": hyp.get("evidence", []),
#                 "prediction": hyp.get("prediction", "")
#             }
#             val = call_validate(hyp_input)
#             st.subheader("Validation Result")
#             if val.get("valid"):
#                 st.success("✅ Hypothesis is VALID")
#             else:
#                 st.error("❌ Hypothesis is INVALID")
#             st.write("Reason:", val.get("reason"))
#             st.write("Proof trace:")
#             for step in val.get("proof_trace", []):
#                 st.write("- " + step)
#             if val.get("warnings"):
#                 st.warning("Warnings: " + "; ".join(val.get("warnings")))
#     except Exception as e:
#         st.error(f"Validation failed: {e}")
#         st.stop()

#     # Step 4: Design experiment if valid
#     if val.get("valid"):
#         try:
#             with st.spinner("Designing experiment..."):
#                 design_input = {
#                     "gap": hyp.get("gap", ""),
#                     "hypothesis": hyp.get("hypothesis", ""),
#                     "evidence": hyp.get("evidence", []),
#                     "prediction": hyp.get("prediction", ""),
#                     "validation_result": val
#                 }
#                 exp = call_design(design_input)
#                 st.subheader("Experiment Blueprint")
#                 st.json(exp)
#                 # Download buttons
#                 st.download_button("Download JSON", json.dumps(exp, indent=2), file_name="experiment.json")
#                 if exp.get("latex"):
#                     st.download_button("Download LaTeX (.tex)", exp.get("latex"), file_name="experiment.tex")
#         except Exception as e:
#             st.error(f"Experiment design failed: {e}")
#     else:
#         st.info("Experiment design skipped because hypothesis is invalid.")











# person_b/dashboard/app.py
import streamlit as st
from utils import call_search, call_generate, call_validate, call_design
import json
import time
import pandas as pd
from pathlib import Path

# Set page config for a professional and wide layout
st.set_page_config(
    page_title="CerebroDiscover: Alzheimer’s Research Pipeline",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a stunning, neuroscience-inspired UI
st.markdown("""
<style>
    /* Main background with gradient */
    .main {
        background: linear-gradient(135deg, #1e1e2f 0%, #2c3e50 100%);
        font-family: 'Roboto', sans-serif;
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
    /* Main content styling */
    .stApp > header {
        background: transparent;
    }
    .card {
        background: #2c3e50;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        color: #ecf0f1;
        margin-bottom: 20px;
        border-left: 4px solid #3498db;
        transition: transform 0.2s ease;
    }
    .card:hover {
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
    /* Ensure text visibility */
    .stMarkdown p, .stMarkdown li, .stMarkdown strong {
        color: #ecf0f1 !important;
    }
    /* Tooltip for help */
    .tooltip {
        position: relative;
        display: inline-block;
    }
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 200px;
        background-color: #2c3e50;
        color: #ecf0f1;
        text-align: center;
        border-radius: 6px;
        padding: 5px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -100px;
        opacity: 0;
        transition: opacity 0.3s;
    }
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
    </style>
""", unsafe_allow_html=True)

# Landing Page
def display_landing_page():
    st.markdown("<h1 class='header'>CerebroDiscover 🧠</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subheader'>Unraveling Alzheimer’s with Neuro-Symbolic AI</p>", unsafe_allow_html=True)
    st.markdown("""
    <div class='card'>
        <p><strong>CerebroDiscover</strong> is a cutting-edge neuro-symbolic AI pipeline designed to accelerate Alzheimer’s research. By integrating semantic search, hypothesis generation, logical validation, and experiment design, it empowers researchers to uncover novel insights into Alzheimer’s pathology.</p>
        <h3>How It Works</h3>
        <ul>
            <li><strong>🔍 Search</strong>: Query a curated database of Alzheimer’s papers.</li>
            <li><strong>🤖 Generate</strong>: Synthesize hypotheses using advanced language models.</li>
            <li><strong>✔️ Validate</strong>: Ensure logical consistency with Z3 theorem proving.</li>
            <li><strong>🧬 Design</strong>: Create actionable experiment blueprints.</li>
        </ul>
        <h3>Hackathon Vision</h3>
        <p>Built for the <strong>[Your Hackathon Name] Hackathon 2025</strong>, CerebroDiscover bridges AI and neuroscience to tackle Alzheimer’s disease. Explore by entering a research question in the sidebar!</p>
        <p><strong>Team</strong>: NeuroAI Innovators | <em>Built with ❤️ by [Your Names]</em><br>
        <strong>Contact</strong>: <a href="mailto:team.email@example.com" style="color: #3498db;">team.email@example.com</a></p>
    </div>
    """, unsafe_allow_html=True)

# Sidebar Controls
with st.sidebar:
    st.markdown("<h2>🧠 Pipeline Controls</h2>", unsafe_allow_html=True)
    st.markdown("<p class='card'>Configure and launch the CerebroDiscover pipeline.</p>", unsafe_allow_html=True)
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
    st.markdown("<div class='tooltip'>Run Pipeline<button class='stButton'><span class='tooltiptext'>Start the full research pipeline</span></button></div>", unsafe_allow_html=True)
    run = st.button("🚀 Run Discovery Pipeline")

if not run:
    display_landing_page()
else:
    progress = st.progress(0)
    st.markdown("<h2 class='subheader'>Pipeline Results</h2>", unsafe_allow_html=True)
    
    # Step 1: Search
    try:
        with st.spinner("🔍 Searching papers..."):
            res = call_search(query, top_k=top_k)
            papers = res["response"].get("papers", [])
            progress.progress(25)
            st.subheader("📄 Papers Retrieved")
            for p in papers:
                st.markdown(f"""
                <div class='card'>
                    <strong>Title</strong>: {p.get('title', 'N/A')} (ID: {p.get('id', 'N/A')})<br>
                    <strong>Abstract</strong>: {p.get('abstract', 'N/A')[:300] + '...' if len(p.get('abstract', '')) > 300 else p.get('abstract', 'N/A')}
                </div>
                """, unsafe_allow_html=True)
            if show_metrics:
                st.markdown(f"<div class='metric-card'>Search Latency: {res['latency']:.2f} s</div>", unsafe_allow_html=True)
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
            st.markdown(f"""
            <div class='card'>
                <strong>Gap</strong>: {hyp.get('gap', 'N/A')}<br>
                <strong>Hypothesis</strong>: {hyp.get('hypothesis', 'N/A')}<br>
                <strong>Prediction</strong>: {hyp.get('prediction', 'N/A')}
            </div>
            """, unsafe_allow_html=True)
            st.markdown("<strong>Evidence</strong>", unsafe_allow_html=True)
            for e in hyp.get("evidence", []):
                st.markdown(f"<div class='card'><p>🔹 {e or 'No evidence'}</p></div>", unsafe_allow_html=True)
            st.markdown("<strong>Logical Rules</strong>", unsafe_allow_html=True)
            rules_df = pd.DataFrame(hyp.get("rules", []), columns=["Rule"])
            st.markdown(f"<div class='card'>{rules_df.to_html(index=False) if not rules_df.empty else '<p>No rules generated</p>'}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='card'><strong>Classification</strong>: {hyp.get('classification', 'Unknown')}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='card'><strong>Further Insights</strong>: {hyp.get('further_data', 'None')}</div>", unsafe_allow_html=True)
            if show_metrics:
                st.markdown(f"<div class='metric-card'>Hypothesis Generation Latency: {call_generate(papers, query)['latency']:.2f} s</div>", unsafe_allow_html=True)
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
            st.markdown(f"<div class='card'><strong>Reason</strong>: {validation_result.get('reason', 'N/A')}</div>", unsafe_allow_html=True)
            st.markdown("<strong>Proof Trace</strong>", unsafe_allow_html=True)
            for step in validation_result.get("proof_trace", []):
                st.markdown(f"<div class='card'><p>🔹 {step or 'No step'}</p></div>", unsafe_allow_html=True)
            if validation_result.get("warnings"):
                st.warning("**Warnings**: " + "; ".join(validation_result.get("warnings", [])))
            if show_metrics:
                st.markdown(f"<div class='metric-card'>Validation Latency: {val['latency']:.2f} s</div>", unsafe_allow_html=True)
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
                st.markdown(f"""
                <div class='card'>
                    <strong>Model</strong>: {exp.get('model', 'N/A')}<br>
                    <strong>Groups</strong>: {', '.join(exp.get('groups', []))}<br>
                    <strong>Sample Size per Group</strong>: {exp.get('n_per_group', 'N/A')}<br>
                    <strong>Duration</strong>: {exp.get('duration_weeks', 'N/A')} weeks<br>
                    <strong>Treatment Route</strong>: {exp.get('treatment_route', 'N/A')}<br>
                    <strong>Outcome Measures</strong>: {', '.join(exp.get('outcome_measures', []))}<br>
                    <strong>Expected Result</strong>: {exp.get('expected_result', 'N/A')}
                </div>
                """, unsafe_allow_html=True)
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
                    st.markdown(f"<div class='metric-card'>Experiment Design Latency: {result['latency']:.2f} s</div>", unsafe_allow_html=True)
                if show_raw_json:
                    with st.expander("Raw Experiment Design Output"):
                        st.json(exp)
        except Exception as e:
            st.error(f"Experiment design failed: {str(e)}")
            st.json(design_input)  # Debug input
    else:
        st.info("Experiment design skipped because hypothesis is invalid or validation failed.")