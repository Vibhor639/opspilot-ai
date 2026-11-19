from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_cloud_agent_workflow():
    response = client.post("/api/v1/agents/investigate", json={
        "question": "Why did our EC2 cloud costs increase?"
    })
    assert response.status_code == 200
    body = response.json()
    assert body["route"] == "cloud"
    assert "Cloud spend" in body["answer"]
    assert body["requires_human_approval"] is True
    assert any(item["agent"] == "supervisor" for item in body["trace"])
    assert any(item["agent"] == "cloud_intelligence_agent" for item in body["trace"])

def test_incident_agent_workflow():
    response = client.post("/api/v1/agents/investigate", json={
        "question": "Show me open incidents and current outages"
    })
    assert response.status_code == 200
    assert response.json()["route"] == "incident"
    assert "INC-1042" in response.json()["answer"]

def test_run_history():
    response = client.post("/api/v1/agents/investigate", json={
        "question": "Show cloud costs"
    })
    thread_id = response.json()["thread_id"]
    history = client.get(f"/api/v1/agents/runs/{thread_id}")
    assert history.status_code == 200
    assert history.json()["thread_id"] == thread_id
