"""Run with: python -m app.mcp_server.server"""
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

from mcp.server.fastmcp import FastMCP
from app.core.config import settings
from app.mcp_server import tools

mcp = FastMCP(
    "OpsPilot MCP Server",
    instructions=(
        "Read-only cloud inventory, cost, utilization, incident and RAG tools. "
        "Live AWS/GCP discovery requires configured least-privilege credentials. "
        "Approval proposals never execute infrastructure changes."
    ),
    host=settings.MCP_HOST,
    port=settings.MCP_PORT,
)

@mcp.tool()
def list_cloud_assets(provider: str | None = None, environment: str | None = None) -> dict:
    """List synthetic demo cloud assets; optional provider and environment filters."""
    return tools.list_cloud_assets(provider, environment)

@mcp.tool()
def get_cloud_asset(asset_id: str) -> dict:
    """Get one synthetic demo cloud asset and associated incidents."""
    return tools.get_cloud_asset(asset_id)

@mcp.tool()
def get_cloud_cost_summary() -> dict:
    """Get synthetic demo month-over-month cloud spend."""
    return tools.get_cloud_cost_summary()

@mcp.tool()
def get_cloud_cost_anomalies(min_change_percent: float = 20.0, min_change_amount: float = 50.0) -> dict:
    """Find synthetic demo services exceeding spend-change thresholds."""
    return tools.get_cloud_cost_anomalies(min_change_percent, min_change_amount)

@mcp.tool()
def get_resource_utilization(classification: str | None = None) -> dict:
    """Get synthetic demo utilization report."""
    return tools.get_resource_utilization(classification)

@mcp.tool()
def list_open_incidents(severity: str | None = None) -> dict:
    """List synthetic demo unresolved incidents."""
    return tools.list_open_incidents(severity)

@mcp.tool()
def search_operational_knowledge(question: str, top_k: int = 5) -> dict:
    """Search indexed runbooks and operational documents with source citations."""
    return tools.search_operational_knowledge(question, top_k)

@mcp.tool()
def request_approval_for_action(action: str, target: str, reason: str) -> dict:
    """Create a human-approval proposal; NEVER executes the requested action."""
    return tools.request_approval_for_action(action, target, reason)

@mcp.tool()
def get_cloud_connection_status() -> dict:
    """Report demo/live mode and whether cloud credential configuration is present."""
    return tools.get_cloud_connection_status()

@mcp.tool()
def list_live_cloud_assets(provider: str, project_id: str | None = None, region: str | None = None) -> dict:
    """List live AWS EC2 or GCP Compute Engine instances using read-only credentials."""
    return tools.list_live_cloud_assets(provider, project_id, region)

@mcp.tool()
def get_live_compute_metrics(provider: str, resource_id: str, lookback_minutes: int = 60, region: str | None = None, project_id: str | None = None) -> dict:
    """Fetch live AWS CloudWatch or GCP Cloud Monitoring CPU metrics."""
    return tools.get_live_compute_metrics(provider, resource_id, lookback_minutes, region, project_id)

@mcp.tool()
def get_live_cost_summary(provider: str, start_date: str, end_date: str, region: str | None = None, project_id: str | None = None) -> dict:
    """Fetch AWS Cost Explorer or GCP BigQuery billing-export costs."""
    return tools.get_live_cost_summary(provider, start_date, end_date, region, project_id)



@mcp.tool()
def create_remediation_approval(action: str, target: str, reason: str) -> dict:
    """Create a persistent human approval request. This tool never executes infrastructure changes."""
    from app.services.approval_service import create_approval
    try:
        return create_approval(action, target, reason, "opspilot-agent")
    except ValueError as exc:
        return {"status": "rejected", "reason": str(exc), "executed": False}


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
