from uuid import uuid4
from app.agents.graph import run_investigation
from app.services.llm_reasoning import plan_investigation
from app.core.config import settings

# Process-local demo run history. Replace with durable DB storage before multi-worker deployment.
_RUNS: dict[str, dict] = {}

def execute_agent_investigation(question: str, thread_id: str | None = None) -> dict:
    run_id = thread_id or str(uuid4())
    llm_key = settings.OPENAI_API_KEY if settings.AGENT_REASONING_MODE.lower() == "llm" else ""
    plan = plan_investigation(question, api_key=llm_key)
    result = run_investigation(
        question, run_id, planned_routes=plan["selected_routes"],
        planning_rationale=plan["rationale"], reasoning_mode=plan["reasoning_mode"],
        reasoning_model=plan.get("model"),
    )
    response = {
        "thread_id": run_id,
        "question": question,
        "route": result.get("route", "unknown"),
        "answer": result.get("final_answer", ""),
        "recommended_actions": result.get("recommended_actions", []),
        "requires_human_approval": result.get("requires_human_approval", True),
        "trace": result.get("agent_trace", []),
        "reasoning_mode": result.get("reasoning_mode", plan["reasoning_mode"]),
        "selected_agents": result.get("selected_routes", plan["selected_routes"]),
        "planning_rationale": plan["rationale"],
        "model": result.get("reasoning_model") or plan.get("model"),
        "warning": (
            "This milestone uses deterministic specialist nodes and synthetic cloud/incident data. "
            "Document retrieval uses the Milestone 3 RAG index. No infrastructure actions are executed."
        ),
    }
    _RUNS[run_id] = response
    return response

def get_agent_run(thread_id: str):
    return _RUNS.get(thread_id)
