import pytest
from app.services import cloud_providers


def test_connection_status_defaults_to_demo_mode(monkeypatch):
    monkeypatch.delenv("CLOUD_MODE", raising=False)
    result = cloud_providers.get_cloud_connection_status()
    assert result["mode"] == "demo"
    assert "safety" in result
    assert "aws" in result and "gcp" in result


def test_live_inventory_is_disabled_in_demo_mode(monkeypatch):
    monkeypatch.setenv("CLOUD_MODE", "demo")
    with pytest.raises(cloud_providers.CloudProviderError, match="Live cloud access is disabled"):
        cloud_providers.list_live_cloud_assets("AWS")


def test_gcp_requires_project_id_in_live_mode(monkeypatch):
    monkeypatch.setenv("CLOUD_MODE", "live")
    monkeypatch.delenv("GCP_PROJECT_ID", raising=False)
    with pytest.raises(cloud_providers.CloudProviderError, match="GCP_PROJECT_ID"):
        cloud_providers.list_live_cloud_assets("GCP")


def test_cost_dates_must_be_valid(monkeypatch):
    monkeypatch.setenv("CLOUD_MODE", "live")
    with pytest.raises(cloud_providers.CloudProviderError, match="YYYY-MM-DD"):
        cloud_providers.get_live_cost_summary("AWS", "not-a-date", "2026-11-15")


def test_end_date_must_follow_start_date(monkeypatch):
    monkeypatch.setenv("CLOUD_MODE", "live")
    with pytest.raises(cloud_providers.CloudProviderError, match="later than"):
        cloud_providers.get_live_cost_summary("AWS", "2026-11-15", "2026-11-15")
