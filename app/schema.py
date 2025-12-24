from pydantic import BaseModel, Field
from typing import Literal, Optional

DecisionType = Literal["GO", "NO-GO", "NEEDS REVIEW"]

class ProjectInput(BaseModel):
    project_name: str = Field(..., min_length=3, max_length=80)
    objective: str = Field(..., min_length=10, max_length=400)

    # Basic constraints
    team_size: int = Field(..., ge=1, le=200)
    duration_weeks: int = Field(..., ge=1, le=104)
    estimated_cost_usd: int = Field(..., ge=0, le=100_000_000)

    # Scales: 1 (low) to 5 (high)
    customer_impact: int = Field(..., ge=1, le=5)
    strategic_alignment: int = Field(..., ge=1, le=5)
    technical_complexity: int = Field(..., ge=1, le=5)
    delivery_risk: int = Field(..., ge=1, le=5)
    compliance_risk: int = Field(..., ge=1, le=5)

    # Optional info
    dependencies_count: int = Field(0, ge=0, le=50)
    has_exec_sponsor: bool = False
    notes: Optional[str] = Field(default="", max_length=600)

class DecisionOutput(BaseModel):
    decision: DecisionType
    score: int  # 0..100
    rationale: list[str]
    recommended_next_steps: list[str]
    guardrails: list[str]
