import os
import streamlit as st
import pandas as pd

from schema import ProjectInput
from decision_engine import run_decision


st.set_page_config(
    page_title="Decision Assistant",
    page_icon="🧭",
    layout="centered",
)

st.title("🧭 Decision Assistant")
st.caption("Simple. Explainable. Built like a real program intake tool.")

with st.expander("What this is", expanded=False):
    st.write(
        """
This tool helps a program leader quickly decide **GO vs NEEDS REVIEW vs NO-GO** using structured inputs.
It produces an explainable score, rationale, next steps, and guardrails.
It is intentionally lightweight. That is the point.
        """.strip()
    )

st.subheader("1) Project intake")

colA, colB = st.columns(2)

with colA:
    project_name = st.text_input("Project name", value="Seller self-service automation")
    objective = st.text_area(
        "Objective (1-3 sentences)",
        value="Reduce manual contacts by automating verification and workflow approvals.",
        height=90,
    )
    team_size = st.number_input("Team size", min_value=1, max_value=200, value=8)
    duration_weeks = st.number_input("Duration (weeks)", min_value=1, max_value=104, value=12)
    estimated_cost_usd = st.number_input("Estimated cost (USD)", min_value=0, max_value=100_000_000, value=150000)

with colB:
    customer_impact = st.slider("Customer impact", 1, 5, 4)
    strategic_alignment = st.slider("Strategic alignment", 1, 5, 5)
    technical_complexity = st.slider("Technical complexity", 1, 5, 3)
    delivery_risk = st.slider("Delivery risk", 1, 5, 3)
    compliance_risk = st.slider("Compliance risk", 1, 5, 2)
    dependencies_count = st.number_input("Dependencies (count)", min_value=0, max_value=50, value=3)
    has_exec_sponsor = st.checkbox("Executive sponsor confirmed", value=True)

notes = st.text_area("Notes (optional)", value="", height=70)

st.subheader("2) Decision")

run = st.button("Generate decision", type="primary")

if run:
    try:
        p = ProjectInput(
            project_name=project_name,
            objective=objective,
            team_size=int(team_size),
            duration_weeks=int(duration_weeks),
            estimated_cost_usd=int(estimated_cost_usd),
            customer_impact=int(customer_impact),
            strategic_alignment=int(strategic_alignment),
            technical_complexity=int(technical_complexity),
            delivery_risk=int(delivery_risk),
            compliance_risk=int(compliance_risk),
            dependencies_count=int(dependencies_count),
            has_exec_sponsor=bool(has_exec_sponsor),
            notes=notes,
        )
        out = run_decision(p)

        st.success(f"Decision: **{out.decision}**")
        st.metric("Score", f"{out.score}/100")

        st.write("### Rationale")
        for r in out.rationale:
            st.write(f"- {r}")

        st.write("### Recommended next steps")
        for s in out.recommended_next_steps:
            st.write(f"- {s}")

        st.write("### Guardrails")
        for g in out.guardrails:
            st.write(f"- {g}")

        st.divider()
        st.write("### Export")
        export = {
            "project_name": p.project_name,
            "objective": p.objective,
            "decision": out.decision,
            "score": out.score,
            "rationale": out.rationale,
            "recommended_next_steps": out.recommended_next_steps,
            "guardrails": out.guardrails,
        }
        st.download_button(
            "Download decision as JSON",
            data=str(export).encode("utf-8"),
            file_name="decision_output.json",
            mime="application/json",
        )

    except Exception as e:
        st.error(f"Input error: {e}")

st.subheader("3) Sample data")
st.caption("A small CSV you can expand. Useful for showing you think about systems and measurement.")

try:
    df = pd.read_csv("data/sample_projects.csv")
    st.dataframe(df, use_container_width=True)
except Exception:
    st.info("Add `data/sample_projects.csv` to display sample data here.")
