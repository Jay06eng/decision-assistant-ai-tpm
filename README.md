# 🧭 AI Decision Assistant  
**Program Management Meets Machine Learning**

An AI-enabled decision system that helps program and business leaders make **GO / NEEDS REVIEW / NO-GO** decisions using structured inputs, ML-informed scoring, and fully explainable recommendations.

This project demonstrates how AI can be applied as a **system**, not a black box. It mirrors real Technical Program Management ownership across ambiguity, risk, and scale.

## 🔗 Live Demo
👉 [DEMO](http://localhost:8501/)

---

## Why this exists
In real organizations, AI initiatives fail less due to modeling and more due to:
- Poor intake quality
- Misaligned stakeholders
- Unclear risk ownership
- Lack of explainability
- Weak execution guardrails

This tool addresses those failure modes directly.

---

## What it does
Given a structured project intake, the system outputs:

- **Decision**: GO, NEEDS REVIEW, or NO-GO  
- **Score**: 0–100 confidence score  
- **Rationale**: Human-readable drivers and risks  
- **Recommended next steps**: Concrete execution actions  
- **Guardrails**: Governance and stage-gate controls  

All outputs are deterministic, explainable, and designed for executive consumption.

---

## How it works (high level)
1. Program inputs are captured via a guided UI
2. Inputs are normalized and scored using weighted signals
3. Risk and value factors are balanced into a final score
4. Decision logic translates score bands into actions
5. Explanations and guardrails are generated automatically

No opaque models. No hidden logic. Trust by design.

---

## Architecture
```mermaid
flowchart TD
  User --> UI[Streamlit Intake UI]
  UI --> Engine[Decision Engine]
  Engine --> Score[Scoring + Explainability]
  Score --> Decision[GO / REVIEW / NO-GO]
  Decision --> UI
  Engine --> Data[(Sample Projects Dataset)]
