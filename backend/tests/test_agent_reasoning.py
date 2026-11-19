from fastapi.testclient import TestClient
from app.main import app
from app.services.llm_reasoning import plan_investigation

client = TestClient(app)


def test_planner_uses_deterministic_fallback_without_api_key():
    plan = plan_investigation("Why is EC2 CPU utilization high?", api_key="")
    assert plan["reasoning_mode"] == "deterministic_fallback"
    assert "cloud" in plan["selected_routes"]


def test_planner_selects_multiple_relevant_specialists():
    plan = plan_investigation(
        "Our production EC2 instance has high CPU. Check the runbook and open incidents.",
        api_key="",
    )
    assert set(plan["selected_routes"]) == {"cloud", "knowledge", "incident"}


def test_planner_always_returns_an_allowed_route():
    plan = plan_investigation("Please investigate this operational question.", api_key="")
    assert plan["selected_routes"]
    assert set(plan["selected_routes"]).issubset({"cloud", "knowledge", "incident"})


def test_reasoning_status_does_not_expose_api_key():
    response = client.get("/api/v1/agents/reasoning/status")
    assert response.status_code == 200
    body = response.json()
    assert body["reasoning_mode"] == "deterministic_fallback"
    assert "api_key" not in body
    assert "OPENAI_API_KEY" not in str(body)


def test_investigation_returns_planning_metadata():
    response = client.post("/api/v1/agents/investigate", json={
        "question": "Our production EC2 instance has high CPU. Check runbook and incidents."
    })
    assert response.status_code == 200
    body = response.json()
    assert body["reasoning_mode"] == "deterministic_fallback"
    assert set(body["selected_agents"]) == {"cloud", "knowledge", "incident"}
    assert body["planning_rationale"]
    assert body["requires_human_approval"] is True
