from pydantic import BaseModel, Field

class AgentInvestigationRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2000)
    thread_id: str | None = Field(default=None, max_length=128)

class AgentTraceItem(BaseModel):
    agent: str
    status: str
    detail: str
    timestamp: str

class AgentInvestigationResponse(BaseModel):
    thread_id: str
    question: str
    route: str
    answer: str
    recommended_actions: list[str]
    requires_human_approval: bool
    trace: list[AgentTraceItem]
    warning: str
    reasoning_mode: str = "deterministic_fallback"
    selected_agents: list[str] = Field(default_factory=list)
    planning_rationale: str = ""
    model: str | None = None
