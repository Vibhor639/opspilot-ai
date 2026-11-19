from typing import Literal
from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Header
from app.schemas.operations import (
    Asset, CostSummary, CostAnomaly, Incident, InvestigationRequest,
    InvestigationResponse, UtilizationReport, DocumentRecord, RAGQueryRequest,
    RAGQueryResponse, MCPToolCallRequest
)
from app.services.inventory import get_assets, get_asset_by_id, get_incidents_for_asset
from app.services.cost_intelligence import build_cost_summary, detect_cost_anomalies
from app.services.utilization import analyze_utilization
from app.services.mock_data import INCIDENTS
from app.services.investigation import investigate
from app.services.rag_service import get_rag_service
from app.core.config import settings

router = APIRouter()

@router.get("/assets", response_model=list[Asset], tags=["cloud"])
def list_assets(
    provider: Literal["AWS", "GCP"] | None = Query(default=None),
    environment: Literal["production", "staging", "development"] | None = Query(default=None),
    resource_type: str | None = Query(default=None),
):
    return get_assets(provider=provider, environment=environment, resource_type=resource_type)

@router.get("/assets/{asset_id}", response_model=Asset, tags=["cloud"])
def asset_detail(asset_id: str):
    asset = get_asset_by_id(asset_id)
    if asset is None:
        raise HTTPException(status_code=404, detail=f"Asset '{asset_id}' was not found.")
    return asset

@router.get("/assets/{asset_id}/incidents", response_model=list[Incident], tags=["operations"])
def asset_incidents(asset_id: str):
    if get_asset_by_id(asset_id) is None:
        raise HTTPException(status_code=404, detail=f"Asset '{asset_id}' was not found.")
    return get_incidents_for_asset(asset_id)

@router.get("/costs/summary", response_model=CostSummary, tags=["cloud"])
def cost_summary():
    return build_cost_summary()

@router.get("/costs/anomalies", response_model=list[CostAnomaly], tags=["cloud"])
def cost_anomalies():
    return detect_cost_anomalies()

@router.get("/utilization", response_model=UtilizationReport, tags=["cloud"])
def utilization_report(classification: Literal["underutilized", "healthy", "overutilized"] | None = Query(default=None)):
    return analyze_utilization(classification)

@router.get("/incidents", response_model=list[Incident], tags=["operations"])
def list_incidents():
    return INCIDENTS

@router.post("/investigations", response_model=InvestigationResponse, tags=["AI"])
def create_investigation(payload: InvestigationRequest):
    if not payload.question.strip():
        raise HTTPException(status_code=422, detail="Question cannot be empty.")
    return investigate(payload.question)

@router.post("/documents", response_model=DocumentRecord, tags=["RAG"])
async def upload_document(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="A filename is required.")
    content = await file.read()
    max_bytes = settings.MAX_UPLOAD_MB * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(status_code=413, detail=f"File exceeds the {settings.MAX_UPLOAD_MB} MB limit.")
    try:
        return get_rag_service().ingest_document(file.filename, content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Document ingestion failed: {exc}") from exc

@router.get("/documents", response_model=list[DocumentRecord], tags=["RAG"])
def list_documents():
    return get_rag_service().list_documents()

@router.delete("/documents/{document_id}", tags=["RAG"])
def delete_document(document_id: str):
    deleted = get_rag_service().delete_document(document_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Document was not found.")
    return {"deleted": True, "document_id": document_id}

@router.post("/rag/query", response_model=RAGQueryResponse, tags=["RAG"])
def query_documents(payload: RAGQueryRequest):
    try:
        return get_rag_service().query(payload.question, payload.top_k)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"RAG query failed: {exc}") from exc


from app.schemas.agents import AgentInvestigationRequest, AgentInvestigationResponse
from app.services.agent_service import execute_agent_investigation, get_agent_run

@router.post("/agents/investigate", response_model=AgentInvestigationResponse, tags=["AI Agents"])
def agent_investigation(payload: AgentInvestigationRequest):
    try:
        return execute_agent_investigation(payload.question, payload.thread_id)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Agent workflow failed: {type(exc).__name__}: {exc}") from exc

@router.get("/agents/runs/{thread_id}", response_model=AgentInvestigationResponse, tags=["AI Agents"])
def agent_run_detail(thread_id: str):
    result = get_agent_run(thread_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Run not found in this server process.")
    return result


from app.mcp_server.client import list_remote_tools, call_remote_tool

@router.get("/mcp/tools", tags=["MCP"] )
async def mcp_list_tools():
    """List tools exposed by the separately running OpsPilot MCP server."""
    try:
        return {"server_url": settings.MCP_SERVER_URL, "tools": await list_remote_tools()}
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"MCP server unavailable: {type(exc).__name__}: {exc}") from exc

@router.post("/mcp/tools/call", tags=["MCP"])
async def mcp_call_tool(payload: MCPToolCallRequest):
    """Call an allowlisted OpsPilot MCP tool through the MCP client."""
    allowed = {
        "list_cloud_assets", "get_cloud_asset", "get_cloud_cost_summary",
        "get_cloud_cost_anomalies", "get_resource_utilization",
        "list_open_incidents", "search_operational_knowledge",
        "request_approval_for_action", "get_cloud_connection_status",
        "list_live_cloud_assets", "get_live_compute_metrics", "get_live_cost_summary", "create_remediation_approval",
    }
    if payload.name not in allowed:
        raise HTTPException(status_code=400, detail="Tool is not in the OpsPilot allowlist.")
    try:
        return await call_remote_tool(payload.name, payload.arguments)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"MCP tool call failed: {type(exc).__name__}: {exc}") from exc


# Milestone 6: live cloud integrations (read-only).
from app.services.cloud_providers import (
    CloudProviderError, get_cloud_connection_status, list_live_cloud_assets,
    get_live_compute_metrics, get_live_cost_summary,
)
from pydantic import BaseModel, Field

class LiveInventoryRequest(BaseModel):
    provider: Literal["AWS", "GCP"]
    project_id: str | None = None
    region: str | None = None

class LiveMetricsRequest(LiveInventoryRequest):
    resource_id: str = Field(min_length=1, max_length=200)
    lookback_minutes: int = Field(default=60, ge=5, le=1440)

class LiveCostRequest(LiveInventoryRequest):
    start_date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    end_date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")

@router.get("/cloud/live/status", tags=["Live Cloud"])
def live_cloud_status():
    """Show cloud mode and credential configuration presence; never returns secrets."""
    return get_cloud_connection_status()

@router.post("/cloud/live/assets", tags=["Live Cloud"])
def live_cloud_assets(payload: LiveInventoryRequest):
    try:
        return list_live_cloud_assets(payload.provider, payload.project_id, payload.region)
    except CloudProviderError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

@router.post("/cloud/live/metrics", tags=["Live Cloud"])
def live_cloud_metrics(payload: LiveMetricsRequest):
    try:
        return get_live_compute_metrics(payload.provider, payload.resource_id, payload.lookback_minutes, payload.region, payload.project_id)
    except CloudProviderError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

@router.post("/cloud/live/costs", tags=["Live Cloud"])
def live_cloud_costs(payload: LiveCostRequest):
    try:
        return get_live_cost_summary(payload.provider, payload.start_date, payload.end_date, payload.region, payload.project_id)
    except CloudProviderError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/agents/reasoning/status", tags=["AI Agents"])
def agent_reasoning_status():
    """Report whether optional LLM planning is enabled without exposing credentials."""
    from app.core.config import settings as app_settings
    enabled = app_settings.AGENT_REASONING_MODE.lower() == "llm" and bool(app_settings.OPENAI_API_KEY)
    return {
        "reasoning_mode": "llm" if enabled else "deterministic_fallback",
        "llm_enabled": enabled,
        "model": app_settings.OPENAI_MODEL if enabled else None,
        "message": ("LLM planning and grounded synthesis are enabled." if enabled
                    else "Deterministic planning and synthesis are active. Configure LLM reasoning settings to opt in."),
    }


# Milestone 8: authenticated human approval workflow (no infrastructure execution).
from secrets import compare_digest
from app.schemas.approvals import (
    ApprovalCreateRequest, ApprovalDecisionRequest, ApprovalRecord, ApprovalAuditEvent
)
from app.services import approval_service

def _require_approval_token(token: str | None) -> None:
    configured = settings.APPROVAL_API_TOKEN
    if not configured:
        raise HTTPException(status_code=503, detail="Approval workflow is not configured. Set APPROVAL_API_TOKEN in backend/.env.")
    if not token or not compare_digest(token, configured):
        raise HTTPException(status_code=401, detail="A valid X-Approval-Token is required.")

@router.post("/approvals", response_model=ApprovalRecord, status_code=201, tags=["Human Approvals"])
def create_approval_request(payload: ApprovalCreateRequest, x_approval_token: str | None = Header(default=None)):
    _require_approval_token(x_approval_token)
    try:
        return approval_service.create_approval(payload.action, payload.target, payload.reason, payload.requested_by)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

@router.get("/approvals", response_model=list[ApprovalRecord], tags=["Human Approvals"])
def list_approval_requests(status: Literal["pending", "approved", "rejected"] | None = Query(default=None), x_approval_token: str | None = Header(default=None)):
    _require_approval_token(x_approval_token)
    return approval_service.list_approvals(status)

@router.get("/approvals/{approval_id}", response_model=ApprovalRecord, tags=["Human Approvals"])
def approval_detail(approval_id: str, x_approval_token: str | None = Header(default=None)):
    _require_approval_token(x_approval_token)
    result = approval_service.get_approval(approval_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Approval request not found.")
    return result

@router.get("/approvals/{approval_id}/audit", response_model=list[ApprovalAuditEvent], tags=["Human Approvals"])
def approval_audit(approval_id: str, x_approval_token: str | None = Header(default=None)):
    _require_approval_token(x_approval_token)
    events = approval_service.get_audit_events(approval_id)
    if events is None:
        raise HTTPException(status_code=404, detail="Approval request not found.")
    return events

def _decide(approval_id: str, payload: ApprovalDecisionRequest, decision: str, token: str | None):
    _require_approval_token(token)
    try:
        result = approval_service.decide_approval(approval_id, decision, payload.decided_by, payload.decision_reason)
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    if result is None:
        raise HTTPException(status_code=404, detail="Approval request not found.")
    return result

@router.post("/approvals/{approval_id}/approve", response_model=ApprovalRecord, tags=["Human Approvals"])
def approve_request(approval_id: str, payload: ApprovalDecisionRequest, x_approval_token: str | None = Header(default=None)):
    return _decide(approval_id, payload, "approved", x_approval_token)

@router.post("/approvals/{approval_id}/reject", response_model=ApprovalRecord, tags=["Human Approvals"])
def reject_request(approval_id: str, payload: ApprovalDecisionRequest, x_approval_token: str | None = Header(default=None)):
    return _decide(approval_id, payload, "rejected", x_approval_token)

@router.post("/approvals/{approval_id}/execute", tags=["Human Approvals"])
def execute_approved_action(approval_id: str, x_approval_token: str | None = Header(default=None)):
    _require_approval_token(x_approval_token)
    approval = approval_service.get_approval(approval_id)
    if approval is None:
        raise HTTPException(status_code=404, detail="Approval request not found.")
    if approval["status"] != "approved":
        raise HTTPException(status_code=409, detail="Only approved requests can be considered for execution.")
    approval_service.record_execution_blocked(approval_id)
    return {"approval_id": approval_id, "status": "execution_disabled", "executed": False,
            "message": "Infrastructure execution is intentionally disabled in Milestone 8. The approval is recorded, but no cloud API is called."}
