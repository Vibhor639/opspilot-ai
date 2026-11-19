"""Shared, read-only operational tools exposed over MCP."""
import json
from app.services.inventory import get_assets, get_asset_by_id, get_incidents_for_asset
from app.services.cost_intelligence import build_cost_summary, detect_cost_anomalies
from app.services.utilization import analyze_utilization
from app.services.mock_data import INCIDENTS
from app.services.rag_service import get_rag_service


def list_cloud_assets(provider: str | None = None, environment: str | None = None) -> dict:
    return {"source": "synthetic_demo_data", "assets": get_assets(provider, environment)}


def get_cloud_asset(asset_id: str) -> dict:
    asset = get_asset_by_id(asset_id)
    if asset is None:
        return {"error": "asset_not_found", "asset_id": asset_id}
    return {"source": "synthetic_demo_data", "asset": asset,
            "related_incidents": get_incidents_for_asset(asset_id)}


def get_cloud_cost_summary() -> dict:
    return {"source": "synthetic_demo_data", "summary": build_cost_summary()}


def get_cloud_cost_anomalies(min_change_percent: float = 20.0, min_change_amount: float = 50.0) -> dict:
    anomalies = detect_cost_anomalies(min_change_percent, min_change_amount)
    return {"source": "synthetic_demo_data", "anomalies": anomalies}


def get_resource_utilization(classification: str | None = None) -> dict:
    return {"source": "synthetic_demo_data", "report": analyze_utilization(classification)}


def list_open_incidents(severity: str | None = None) -> dict:
    items = [i for i in INCIDENTS if i["status"] != "resolved"]
    if severity:
        items = [i for i in items if i["severity"] == severity]
    return {"source": "synthetic_demo_data", "incidents": items}


def search_operational_knowledge(question: str, top_k: int = 5) -> dict:
    if not question.strip():
        return {"error": "question_required"}
    result = get_rag_service().query(question, top_k=max(1, min(top_k, 10)))
    return {"question": result["question"], "answer": result["answer"],
            "sources": result["sources"], "generation_mode": result["generation_mode"],
            "warning": result.get("warning")}


def request_approval_for_action(action: str, target: str, reason: str) -> dict:
    """Create a proposal only. This tool never performs infrastructure changes."""
    allowed = {"restart_instance", "resize_instance", "scale_service", "stop_instance"}
    if action not in allowed:
        return {"status": "rejected", "reason": "Unsupported action type."}
    if not target.strip() or not reason.strip():
        return {"status": "rejected", "reason": "Target and reason are required."}
    return {
        "status": "approval_required", "proposal_id": "proposal-pending-review",
        "action": action, "target": target, "reason": reason,
        "executed": False,
        "message": "Proposal recorded for demonstration only. No cloud API was called. "
                   "A real approval workflow and provider integration are required before execution."
    }


def tool_result_to_json(result) -> str:
    """Serialize MCP tool results for predictable client responses."""
    if hasattr(result, "model_dump"):
        result = result.model_dump()
    return json.dumps(result, default=str)


# Milestone 6: read-only live cloud provider tools.
from app.services import cloud_providers

def get_cloud_connection_status() -> dict:
    return cloud_providers.get_cloud_connection_status()

def list_live_cloud_assets(provider: str, project_id: str | None = None, region: str | None = None) -> dict:
    return cloud_providers.list_live_cloud_assets(provider, project_id, region)

def get_live_compute_metrics(provider: str, resource_id: str, lookback_minutes: int = 60, region: str | None = None, project_id: str | None = None) -> dict:
    return cloud_providers.get_live_compute_metrics(provider, resource_id, lookback_minutes, region, project_id)

def get_live_cost_summary(provider: str, start_date: str, end_date: str, region: str | None = None, project_id: str | None = None) -> dict:
    return cloud_providers.get_live_cost_summary(provider, start_date, end_date, region, project_id)
