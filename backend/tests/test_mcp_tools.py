from app.mcp_server import tools


def test_list_cloud_assets_returns_demo_assets():
    result = tools.list_cloud_assets(provider="AWS")
    assert result["source"] == "synthetic_demo_data"
    assert result["assets"]
    assert all(item["provider"] == "AWS" for item in result["assets"])


def test_cost_anomalies_are_returned():
    result = tools.get_cloud_cost_anomalies()
    assert result["anomalies"]
    assert result["anomalies"][0]["change_percent"] >= 20


def test_asset_lookup_includes_related_incidents():
    result = tools.get_cloud_asset("i-ops-001")
    assert result["asset"]["id"] == "i-ops-001"
    assert result["related_incidents"]


def test_approval_tool_never_executes_action():
    result = tools.request_approval_for_action(
        "restart_instance", "i-ops-001", "Investigate high CPU"
    )
    assert result["status"] == "approval_required"
    assert result["executed"] is False


def test_unsupported_action_is_rejected():
    result = tools.request_approval_for_action("delete_account", "prod", "cleanup")
    assert result["status"] == "rejected"
