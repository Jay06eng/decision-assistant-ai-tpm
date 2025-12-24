from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple
import numpy as np
from .schema import ProjectInput, DecisionOutput

@dataclass(frozen=True)
class Weights:
    # Positive signals
    customer_impact: float = 0.22
    strategic_alignment: float = 0.22
    exec_sponsor: float = 0.10

    # Risk signals (subtract)
    technical_complexity: float = 0.14
    delivery_risk: float = 0.16
    compliance_risk: float = 0.10
    dependencies: float = 0.06

    # Size/effort signals (subtract lightly)
    team_size: float = 0.03
    duration: float = 0.04
    cost: float = 0.03

DEFAULT_WEIGHTS = Weights()

def _scale_1_to_5(x: int) -> float:
    # Convert 1..5 into 0..1
    return (x - 1) / 4.0

def _clip_0_1(x: float) -> float:
    return float(np.clip(x, 0.0, 1.0))

def _normalize_cost(cost_usd: int) -> float:
    # Simple normalization: 0..5M maps roughly to 0..1, saturates after
    return _clip_0_1(cost_usd / 5_000_000)

def _normalize_duration(weeks: int) -> float:
    return _clip_0_1(weeks / 52)

def _normalize_team(team_size: int) -> float:
    return _clip_0_1(team_size / 50)

def _normalize_dependencies(n: int) -> float:
    return _clip_0_1(n / 15)

def score_project(p: ProjectInput, w: Weights = DEFAULT_WEIGHTS) -> Tuple[int, List[str]]:
    rationale: List[str] = []

    pos = 0.0
    neg = 0.0

    ci = _scale_1_to_5(p.customer_impact)
    sa = _scale_1_to_5(p.strategic_alignment)
    tc = _scale_1_to_5(p.technical_complexity)
    dr = _scale_1_to_5(p.delivery_risk)
    cr = _scale_1_to_5(p.compliance_risk)

    dep = _normalize_dependencies(p.dependencies_count)
    team = _normalize_team(p.team_size)
    dur = _normalize_duration(p.duration_weeks)
    cost = _normalize_cost(p.estimated_cost_usd)
    sponsor = 1.0 if p.has_exec_sponsor else 0.0

    pos += w.customer_impact * ci
    pos += w.strategic_alignment * sa
    pos += w.exec_sponsor * sponsor

    neg += w.technical_complexity * tc
    neg += w.delivery_risk * dr
    neg += w.compliance_risk * cr
    neg += w.dependencies * dep
    neg += w.team_size * team
    neg += w.duration * dur
    neg += w.cost * cost

    raw = pos - neg

    # Convert to 0..100 with a smooth mapping.
    # raw around 0 means ~50.
    score = int(round(100 * (1 / (1 + np.exp(-6 * raw)))))

    # Explainability. Trigger top reasons.
    if p.customer_impact >= 4:
        rationale.append("High customer impact increases priority and expected ROI.")
    if p.strategic_alignment >= 4:
        rationale.append("Strong strategic alignment supports funding and stakeholder commitment.")
    if p.has_exec_sponsor:
        rationale.append("Executive sponsorship reduces coordination risk and accelerates decisions.")

    if p.delivery_risk >= 4:
        rationale.append("High delivery risk suggests you need stronger plan, milestones, and contingency.")
    if p.technical_complexity >= 4:
        rationale.append("High technical complexity suggests discovery, architecture review, and phased rollout.")
    if p.compliance_risk >= 4:
        rationale.append("High compliance risk requires early security and legal review with clear controls.")
    if p.dependencies_count >= 8:
        rationale.append("Many dependencies increase schedule risk. Consider de-risking or reducing scope.")
    if p.duration_weeks >= 26:
        rationale.append("Long duration increases risk. Consider an MVP milestone or phased delivery.")

    if not rationale:
        rationale.append("Signals are balanced. Decision depends on risk controls and milestone clarity.")

    return score, rationale

def decide(score: int, p: ProjectInput) -> Tuple[str, List[str], List[str]]:
    guardrails = [
        "Define success metrics and leading indicators before execution.",
        "Require a written risk register with owners and mitigation dates.",
        "Use stage gates for funding. Discovery, MVP, Scale.",
    ]

    next_steps: List[str] = []

    # Decision thresholds tuned for a simple, intuitive demo.
    if score >= 70:
        decision = "GO"
        next_steps = [
            "Lock success metrics. North Star plus 3 supporting KPIs.",
            "Create a milestone plan. Discovery, MVP, rollout.",
            "Confirm resourcing and ownership across teams.",
        ]
        if p.delivery_risk >= 4 or p.technical_complexity >= 4:
            next_steps.insert(0, "Run a 2-week discovery sprint to validate approach and reduce risk.")
        return decision, next_steps, guardrails

    if 45 <= score < 70:
        decision = "NEEDS REVIEW"
        next_steps = [
            "Identify the top 3 risks and create a mitigation plan with owners.",
            "Reduce scope to an MVP. One user journey, one workflow.",
            "Confirm dependency commitments in writing.",
            "Add instrumentation and an A/B test plan if user-facing.",
        ]
        if p.compliance_risk >= 4:
            next_steps.insert(0, "Schedule security and compliance review within 7 days.")
        return decision, next_steps, guardrails

    decision = "NO-GO"
    next_steps = [
        "Write a one-page alternative plan. Smaller scope or different approach.",
        "Re-evaluate after risks are reduced or strategy changes.",
        "If still needed, run a discovery spike to validate feasibility and cost.",
    ]
    if p.customer_impact >= 4 and p.strategic_alignment >= 4:
        next_steps.insert(0, "This looks valuable, but current risk is too high. De-risk with discovery and an MVP.")
    return decision, next_steps, guardrails

def run_decision(p: ProjectInput) -> DecisionOutput:
    score, rationale = score_project(p)
    decision, next_steps, guardrails = decide(score, p)

    return DecisionOutput(
        decision=decision,
        score=score,
        rationale=rationale,
        recommended_next_steps=next_steps,
        guardrails=guardrails,
    )
