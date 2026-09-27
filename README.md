# 🎯 AgentEval-Gate: Automated AI Regression & Quality Benchmarking Suite

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat&logo=python&logoColor=white)
![Ollama](https://img.shields.io/badge/Local_LLM-Ollama-black?style=flat)
![Framework](https://img.shields.io/badge/UI-Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Discipline](https://img.shields.io/badge/Discipline-AI_Evals_%26_Gating-orange)

> An open-source model evaluation harness that uses local **LLM-as-a-Judge** scoring against a **Golden Benchmark Dataset** to automate CI/CD release gating and prevent AI regressions.

---

## 📌 The Problem: The "Vibes-Based" Deployment Bottleneck

When engineering teams update a system prompt, swap model weights, or change retrieval context, they face a critical operational dilemma:
- **Unquantified Regressions:** Subtle changes can cause a model to begin hallucinating non-existent parameters or dropping schema fields.
- **Manual QA Exhaustion:** Reviewing edge cases by hand does not scale across multi-agent pipelines.
- **Lack of Objective Gating:** Release decisions are often made based on anecdotal testing ("it feels good") rather than quantitative thresholds.

---

## 💡 The Solution: Quantitative AI Evaluation & Gating

**AgentEval-Gate** replaces subjective prompt testing with an automated, reproducible benchmark harness:

```mermaid
flowchart TD
    A[Golden Benchmark Dataset] --> B[Target Model / Agent Run]
    B --> C[Latency & Response Profiler]
    C --> D[LLM-as-a-Judge Engine]
    
    subgraph Evaluation Rubrics
        D --> D1[Schema Compliance]
        D --> D2[Hallucination Traps]
        D --> D3[Edge Case Recovery]
        D --> D4[Observability Standards]
    end
    
    D1 & D2 & D3 & D4 --> E[Automated Release Gate]
    E -->|Score >= Threshold| F[✅ RELEASE APPROVED]
    E -->|Score < Threshold| G[❌ RELEASE BLOCKED: REGRESSION DETECTED]
