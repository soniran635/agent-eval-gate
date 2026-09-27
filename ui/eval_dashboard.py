import os
import sys
import json

# Ensure project root is in Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from src.models import EvalTestCase
from src.eval_engine import EvalEngine

st.set_page_config(page_title="AgentEval-Gate | AI Regression Suite", layout="wide", page_icon="🎯")

st.title("🎯 AgentEval-Gate: Automated AI Regression & Quality Benchmarking")
st.markdown("**Enterprise Model Evaluation Harness | LLM-as-a-Judge | CI/CD Release Gating** | *100% Free & Open-Source*")

# Sidebar settings
with st.sidebar:
    st.header("⚙️ Evaluation Parameters")
    model_name = st.selectbox("Target Model", ["llama3.2:3b", "llama3.2:1b"], index=0)
    min_accuracy = st.slider("Min Accuracy Threshold (%)", min_value=50, max_value=100, value=75, step=5) / 100.0
    st.info("Runs the Golden Dataset benchmarks using local Ollama and automated LLM-as-a-Judge scoring.")

# Load Golden Dataset
with open("benchmarks/golden_dataset.json", "r") as f:
    raw_tests = json.load(f)
test_cases = [EvalTestCase(**t) for t in raw_tests]

st.subheader(f"📋 Golden Benchmark Suite ({len(test_cases)} Test Cases)")
with st.expander("View Benchmark Test Cases & Rubrics", expanded=False):
    st.json(raw_tests)

run_button = st.button("🚀 Run Automated Regression Benchmark Suite", type="primary", use_container_width=True)

if run_button:
    engine = EvalEngine(model_name=model_name)
    
    with st.status(f"Executing benchmarks against `{model_name}`...", expanded=True) as status:
        results, summary = engine.evaluate_suite(test_cases, accuracy_threshold=min_accuracy)
        status.update(label="Evaluation Complete!", state="complete", expanded=False)

    # 1. Release Gating Decision Metrics
    st.subheader("🏁 Automated Release Gate Verdict")
    m1, m2, m3, m4 = st.columns(4)
    
    with m1:
        st.metric(label="Overall Accuracy", value=f"{int(summary.overall_accuracy * 100)}%", delta=f"{summary.passed_tests}/{summary.total_tests} Passed")
    with m2:
        st.metric(label="Average Latency", value=f"{summary.avg_latency_sec}s")
    with m3:
        st.metric(label="Hallucination Rate", value=f"{int(summary.hallucination_rate * 100)}%", delta="Clean" if summary.hallucination_rate == 0 else "High Risk", delta_color="inverse")
    with m4:
        if summary.release_verdict == "APPROVED":
            st.success("### ✅ RELEASE APPROVED")
        else:
            st.error("### ❌ RELEASE BLOCKED")

    if summary.blocking_reasons:
        st.error(f"**Gating Violations:** {', '.join(summary.blocking_reasons)}")
    else:
        st.success("**Gating Policy Satisfied:** Model adheres to all schema, safety, and latency thresholds.")

    st.divider()

    # 2. Detailed Test-by-Test Audit
    st.subheader("🔍 Detailed LLM-as-a-Judge Scorecard")
    for res in results:
        status_icon = "✅" if res.passed else "❌"
        with st.expander(f"{status_icon} `{res.test_id}`: {res.category} (Latency: {res.latency_sec}s | Score: {int(res.score * 100)}%)"):
            st.markdown(f"**Judge Reasoning:** {res.judge_reasoning}")
            st.markdown("**Model Output:**")
            st.code(res.model_response)
