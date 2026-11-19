from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200 and r.json()["status"] == "ok"

def test_asset_inventory_and_filter():
    r = client.get("/api/v1/assets")
    assert r.status_code == 200 and len(r.json()) == 5
    aws = client.get("/api/v1/assets", params={"provider":"AWS"})
    assert aws.status_code == 200
    assert all(a["provider"] == "AWS" for a in aws.json())

def test_asset_detail_and_404():
    assert client.get("/api/v1/assets/i-ops-001").status_code == 200
    assert client.get("/api/v1/assets/not-real").status_code == 404

def test_cost_summary_and_anomaly():
    summary = client.get("/api/v1/costs/summary")
    assert summary.status_code == 200
    assert summary.json()["current_month"] > summary.json()["previous_month"]
    anomalies = client.get("/api/v1/costs/anomalies")
    assert anomalies.status_code == 200
    assert any(a["service"] == "EC2" for a in anomalies.json())

def test_utilization():
    r = client.get("/api/v1/utilization")
    assert r.status_code == 200
    assert r.json()["total_assets"] == 5
    assert r.json()["underutilized"] >= 1
    assert r.json()["overutilized"] >= 1

def test_incident_correlation():
    r = client.get("/api/v1/assets/i-ops-001/incidents")
    assert r.status_code == 200
    assert any(i["id"] == "INC-1042" for i in r.json())

def test_investigation():
    r = client.post("/api/v1/investigations", json={"question":"Why did EC2 costs increase?"})
    assert r.status_code == 200
    assert r.json()["requires_human_approval"] is True
