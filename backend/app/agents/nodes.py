from datetime import datetime, timezone
from app.agents.state import OpsPilotState
from app.services.cost_intelligence import (
    build_cost_summary,
    detect_cost_anomalies,
    build_resource_cost_attribution,
)
from app.services.utilization import analyze_utilization
from app.services.mock_data import INCIDENTS
from app.services.rag_service import get_rag_service
from app.services.llm_reasoning import synthesize_with_llm
from app.core.config import settings

def _trace(state: OpsPilotState, agent: str, status: str, detail: str) -> list[dict]:
    return [{
        "agent": agent, "status": status, "detail": detail,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }]

def supervisor_node(state: OpsPilotState) -> dict:
    question = state["question"].lower()
    wants_docs = any(term in question for term in [
        "document", "runbook", "manual", "documentation", "recommend", "procedure",
        "how do i", "how should", "steps", "policy", "guide"
    ])
    wants_cloud = any(term in question for term in [
        "cost", "spend", "billing", "ec2", "aws", "gcp", "cloud", "cpu",
        "memory", "utilization", "resource", "instance", "infrastructure"
    ])
    wants_incidents = any(term in question for term in [
        "incident", "outage", "error", "latency", "failure", "ticket", "alert"
    ])

    routes = state.get("planned_routes") or []
    if not routes and wants_cloud:
        routes.append("cloud")
    if not state.get("planned_routes"):
        if wants_docs:
            routes.append("knowledge")
        if wants_incidents:
            routes.append("incident")
        if not routes:
            routes = ["knowledge"]

    route = "multi" if len(routes) > 1 else routes[0]
    rationale = state.get("planning_rationale", "Deterministic supervisor selected routes.")
    trace = _trace(state, "supervisor", "completed", f"Selected specialist route(s): {', '.join(routes)}. {rationale}")
    return {"route": route, "selected_routes": routes, "agent_trace": trace}


def cloud_agent_node(state: OpsPilotState) -> dict:
    costs = build_cost_summary()
    anomalies = detect_cost_anomalies()
    utilization = analyze_utilization()
    attribution = build_resource_cost_attribution()

    findings = [
        {"type": "cost_summary", "data": costs},
        {"type": "cost_anomalies", "data": anomalies},
        {"type": "resource_utilization", "data": utilization},
        {"type": "resource_cost_attribution", "data": attribution},
    ]

    return {
        "cloud_findings": findings,
        "agent_trace": _trace(
            state,
            "cloud_intelligence_agent",
            "completed",
            "Analysed synthetic service costs, resource-level cost attribution, "
            "cost anomalies, and utilization data.",
        ),
    }


def knowledge_agent_node(state: OpsPilotState) -> dict:
    try:
        result = get_rag_service().query(state["question"], top_k=4)
        findings = result.get("sources", [])
        detail = f"Retrieved {len(findings)} document passage(s); generation mode: {result.get('generation_mode')}."
    except Exception as exc:
        findings = []
        detail = f"Knowledge retrieval unavailable: {type(exc).__name__}. Upload and index documents first."
    return {
        "knowledge_findings": findings,
        "agent_trace": _trace(state, "knowledge_agent", "completed", detail)
    }

def incident_agent_node(state: OpsPilotState) -> dict:
    incidents = [item for item in INCIDENTS if item["status"] != "resolved"]
    findings = [{
        "incident_id": item["id"],
        "title": item["title"],
        "severity": item["severity"],
        "status": item["status"],
        "affected_asset_ids": item["affected_asset_ids"],
    } for item in incidents]
    return {
        "incident_findings": findings,
        "agent_trace": _trace(state, "incident_agent", "completed",
                              f"Reviewed {len(findings)} unresolved synthetic incident(s).")
    }

def synthesis_node(state: OpsPilotState) -> dict:
    sections = []
    actions = []
    cloud = state.get("cloud_findings", [])
    knowledge = state.get("knowledge_findings", [])
    incidents = state.get("incident_findings", [])

    if cloud:
        for item in cloud:
            kind = item["type"]
            data = item["data"]
            if kind == "cost_summary":
                sections.append(
                    f"Cloud spend: ${data['current_month']:,.2f} this month versus "
                    f"${data['previous_month']:,.2f} previously "
                    f"({data['change_percent']:.1f}% change; synthetic dataset)."
                )
            elif kind == "cost_anomalies":
                if data:
                    sections.append("Potential cost increases: " + "; ".join(
                        f"{x['service']} +{x['change_percent']:.1f}% (${x['change_amount']:,.2f})"
                        for x in data
                    ))
                else:
                    sections.append("No cost increases met the configured demo thresholds.")
            elif kind == "resource_utilization":
                sections.append(
                    f"Resource utilization: {data['underutilized']} underutilized, "
                    f"{data['healthy']} healthy, {data['overutilized']} overutilized."
                )
                actions.extend(
                    x["recommendation"] for x in data["items"]
                    if x["classification"] in ("underutilized", "overutilized")
                )

            elif kind == "resource_cost_attribution":
                sections.append(
                    f"Resource-level attribution: {data['tracked_resource_count']} "
                    f"tracked resources account for "
                    f"${data['tracked_current_month']:,.2f} this month versus "
                    f"${data['tracked_previous_month']:,.2f} previously, "
                    f"an increase of ${data['tracked_change_amount']:,.2f} "
                    f"({data['tracked_change_percent']:.1f}%)."
                )

                sections.append(
                    f"Unattributed cloud spend: "
                    f"${data['unattributed_current_month']:,.2f} this month "
                    f"versus ${data['unattributed_previous_month']:,.2f} previously. "
                    f"The unattributed increase is "
                    f"${data['unattributed_change_amount']:,.2f}. "
                    f"This spend is not assigned to the five tracked assets."
                )

                if data["top_cost_increases"]:
                    sections.append(
                        "Top resource-level cost increases: "
                        + "; ".join(
                            f"{item['asset_name']} "
                            f"({item['asset_id']}) +"
                            f"${item['change_amount']:,.2f} "
                            f"({item['change_percent']:.1f}%), "
                            f"CPU {item['cpu_utilization_percent']:.0f}%, "
                            f"memory {item['memory_utilization_percent']:.0f}%"
                            for item in data["top_cost_increases"]
                        )
                    )

                    for item in data["top_cost_increases"]:
                        if (
                            item["cpu_utilization_percent"] < 20
                            and item["memory_utilization_percent"] < 35
                        ):
                            actions.append(
                                f"Review rightsizing opportunities for "
                                f"{item['asset_name']} ({item['asset_id']}), "
                                f"which increased by ${item['change_amount']:,.2f} "
                                f"despite low CPU and memory utilization. "
                                f"Validate workload patterns before resizing."
                            )
                        elif item["change_percent"] >= 20:
                            actions.append(
                                f"Investigate the cost increase for "
                                f"{item['asset_name']} ({item['asset_id']}): "
                                f"+${item['change_amount']:,.2f} "
                                f"({item['change_percent']:.1f}%)."
                            )

                if data["unattributed_change_amount"] > 0:
                    actions.append(
                        f"Investigate ${data['unattributed_change_amount']:,.2f} "
                        f"in additional cloud spend not attributed to tracked assets. "
                        f"Reconcile service-level billing with the asset inventory."
                    )


    if knowledge:
        sections.append("Relevant documentation passages were retrieved:")
        for source in knowledge:
            page = f", page {source['page_number']}" if source.get("page_number") else ""
            sections.append(
                f"[{source.get('citation', 'source')}] {source['filename']}{page}: {source['text']}"
            )
    else:
        sections.append("No relevant indexed document passages were available for this question.")

    if incidents:
        sections.append("Unresolved incidents: " + "; ".join(
            f"{x['incident_id']} ({x['severity']}): {x['title']}" for x in incidents
        ))
    else:
        sections.append("No unresolved incidents were returned.")

    actions.extend([
        "Validate all findings against live provider telemetry and current operational records.",
        "Obtain service-owner and change-management approval before any production change."
    ])
    answer = "\n\n".join(sections)
    recommended_actions = list(dict.fromkeys(actions))
    llm_key = settings.OPENAI_API_KEY if settings.AGENT_REASONING_MODE.lower() == "llm" else ""
    llm_result = synthesize_with_llm(
        state.get("question", ""),
        {"cloud_findings": cloud, "knowledge_findings": knowledge, "incident_findings": incidents},
        api_key=llm_key,
    )
    if llm_result:
        answer = llm_result["answer"]
        recommended_actions = list(dict.fromkeys(llm_result["recommended_actions"] + recommended_actions))
        reasoning_mode = "llm"
        reasoning_model = llm_result.get("model")
        detail = "Combined specialist evidence using LLM synthesis with source-grounding constraints."
    else:
        reasoning_mode = state.get("reasoning_mode", "deterministic_fallback")
        reasoning_model = None
        detail = "Combined specialist outputs using deterministic evidence-grounded synthesis."
    trace = _trace(state, "synthesis_agent", "completed", detail)
    return {
        "final_answer": answer,
        "recommended_actions": recommended_actions,
        "requires_human_approval": True,
        "reasoning_mode": reasoning_mode,
        "reasoning_model": reasoning_model,
        "agent_trace": trace
    }

def error_node(state: OpsPilotState) -> dict:
    return {
        "error": state.get("error", "The workflow could not complete."),
        "final_answer": "The investigation workflow encountered an error. Review the execution trace and retry.",
        "recommended_actions": [],
        "requires_human_approval": True,
        "agent_trace": _trace(state, "error_handler", "failed", state.get("error", "Unknown error"))
    }
