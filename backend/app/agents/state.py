from typing import TypedDict, Any, Annotated
import operator

class OpsPilotState(TypedDict, total=False):
    question: str
    thread_id: str
    route: str
    selected_routes: list[str]
    planned_routes: list[str]
    planning_rationale: str
    reasoning_mode: str
    reasoning_model: str | None
    cloud_findings: list[dict[str, Any]]
    knowledge_findings: list[dict[str, Any]]
    incident_findings: list[dict[str, Any]]
    agent_trace: Annotated[list[dict[str, Any]], operator.add]
    final_answer: str
    recommended_actions: list[str]
    requires_human_approval: bool
    error: str
