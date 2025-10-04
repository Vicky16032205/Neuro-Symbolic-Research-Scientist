# person_b/dashboard/app.py
import streamlit as st
from utils import call_search, call_generate, call_validate, call_design
import json
import time

st.set_page_config(page_title="CerebroDiscover Dashboard", layout="wide")

st.title("CerebroDiscover — Neuro-Symbolic Research Scientist (Alzheimer's)")

with st.sidebar:
    st.header("Pipeline Controls")
    query = st.text_input("Research question", value="Why do anti-amyloid drugs fail?")
    top_k = st.number_input("Top-k papers", min_value=1, max_value=10, value=3)
    run = st.button("Run Discovery Pipeline")

if run:
    st.info("Running pipeline...")
    # Step 1: Search
    try:
        with st.spinner("Searching papers..."):
            res = call_search(query, top_k=top_k)
            papers = res.get("papers", [])
            st.subheader("Papers retrieved")
            for p in papers:
                st.markdown(f"**{p.get('title')}** (id: {p.get('id')})")
                st.write(p.get("abstract")[:500] + "...")
    except Exception as e:
        st.error(f"Search failed: {e}")
        st.stop()

    # Step 2: Generate Hypothesis
    try:
        with st.spinner("Generating hypothesis..."):
            hyp = call_generate(papers)
            st.subheader("Generated Hypothesis")
            st.json(hyp)
    except Exception as e:
        st.error(f"Hypothesis generation failed: {e}")
        st.stop()

    # Step 3: Validate
    try:
        with st.spinner("Validating hypothesis (Z3)..."):
            hyp_input = {
                "gap": hyp.get("gap", ""),
                "hypothesis": hyp.get("hypothesis", ""),
                "evidence": hyp.get("evidence", []),
                "prediction": hyp.get("prediction", "")
            }
            val = call_validate(hyp_input)
            st.subheader("Validation Result")
            if val.get("valid"):
                st.success("✅ Hypothesis is VALID")
            else:
                st.error("❌ Hypothesis is INVALID")
            st.write("Reason:", val.get("reason"))
            st.write("Proof trace:")
            for step in val.get("proof_trace", []):
                st.write("- " + step)
            if val.get("warnings"):
                st.warning("Warnings: " + "; ".join(val.get("warnings")))
    except Exception as e:
        st.error(f"Validation failed: {e}")
        st.stop()

    # Step 4: Design experiment if valid
    if val.get("valid"):
        try:
            with st.spinner("Designing experiment..."):
                design_input = {
                    "gap": hyp.get("gap", ""),
                    "hypothesis": hyp.get("hypothesis", ""),
                    "evidence": hyp.get("evidence", []),
                    "prediction": hyp.get("prediction", ""),
                    "validation_result": val
                }
                exp = call_design(design_input)
                st.subheader("Experiment Blueprint")
                st.json(exp)
                # Download buttons
                st.download_button("Download JSON", json.dumps(exp, indent=2), file_name="experiment.json")
                if exp.get("latex"):
                    st.download_button("Download LaTeX (.tex)", exp.get("latex"), file_name="experiment.tex")
        except Exception as e:
            st.error(f"Experiment design failed: {e}")
    else:
        st.info("Experiment design skipped because hypothesis is invalid.")