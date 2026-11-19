from langgraph.graph import StateGraph, START, END
from app.agents.state import OpsPilotState
from app.agents.nodes import (
    supervisor_node, cloud_agent_node, knowledge_agent_node,
    incident_agent_node, synthesis_node
)

def _route_after_supervisor(state: OpsPilotState):
    routes = state.get("selected_routes", ["knowledge"])
    return routes

def build_investigation_graph():
    graph = StateGraph(OpsPilotState)
    graph.add_node("supervisor", supervisor_node)
    graph.add_node("cloud_agent", cloud_agent_node)
    graph.add_node("knowledge_agent", knowledge_agent_node)
    graph.add_node("incident_agent", incident_agent_node)
    graph.add_node("synthesis", synthesis_node)

    graph.add_edge(START, "supervisor")
    graph.add_conditional_edges(
        "supervisor",
        _route_after_supervisor,
        {
            "cloud": "cloud_agent",
            "knowledge": "knowledge_agent",
            "incident": "incident_agent",
        },
    )

    # Every selected specialist returns to a shared synthesis node.
    graph.add_edge("cloud_agent", "synthesis")
    graph.add_edge("knowledge_agent", "synthesis")
    graph.add_edge("incident_agent", "synthesis")
    graph.add_edge("synthesis", END)
    return graph.compile()

investigation_graph = build_investigation_graph()

def run_investigation(question: str, thread_id: str | None = None, planned_routes: list[str] | None = None, planning_rationale: str = "", reasoning_mode: str = "deterministic_fallback", reasoning_model: str | None = None) -> dict:
    initial: OpsPilotState = {
        "question": question,
        "thread_id": thread_id or "local-session",
        "agent_trace": [],
        "planned_routes": planned_routes or [],
        "planning_rationale": planning_rationale,
        "reasoning_mode": reasoning_mode,
        "reasoning_model": reasoning_model,
    }
    result = investigation_graph.invoke(initial)
    return result
