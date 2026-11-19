import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)
TOKEN = "test-approval-token"

@pytest.fixture(autouse=True)
def approval_config(tmp_path):
    old_token, old_path = settings.APPROVAL_API_TOKEN, settings.APPROVAL_DB_PATH
    object.__setattr__(settings, "APPROVAL_API_TOKEN", TOKEN)
    object.__setattr__(settings, "APPROVAL_DB_PATH", str(tmp_path / "approvals.db"))
    yield
    object.__setattr__(settings, "APPROVAL_API_TOKEN", old_token)
    object.__setattr__(settings, "APPROVAL_DB_PATH", old_path)


def create_request():
    return client.post("/api/v1/approvals", headers={"X-Approval-Token": TOKEN}, json={
        "action": "restart_instance", "target": "i-demo-001",
        "reason": "Sustained high CPU requires service-owner review.", "requested_by": "ops-engineer"
    })


def test_approval_creation_requires_token():
    response = client.post("/api/v1/approvals", json={
        "action": "restart_instance", "target": "i-demo-001",
        "reason": "Sustained high CPU requires review.", "requested_by": "ops-engineer"
    })
    assert response.status_code == 401

def test_create_approval_starts_pending_and_not_executed():
    response = create_request()
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "pending"
    assert body["executed"] is False

def test_approve_request_and_audit_history():
    created = create_request().json()
    approval_id = created["approval_id"]
    response = client.post(f"/api/v1/approvals/{approval_id}/approve", headers={"X-Approval-Token": TOKEN}, json={
        "decided_by": "service-owner", "decision_reason": "Reviewed evidence; approved for change window."
    })
    assert response.status_code == 200
    assert response.json()["status"] == "approved"
    events = client.get(f"/api/v1/approvals/{approval_id}/audit", headers={"X-Approval-Token": TOKEN}).json()
    assert [event["event_type"] for event in events] == ["requested", "approved"]

def test_reject_request_records_reason():
    created = create_request().json()
    response = client.post(f"/api/v1/approvals/{created['approval_id']}/reject", headers={"X-Approval-Token": TOKEN}, json={
        "decided_by": "service-owner", "decision_reason": "Insufficient evidence; investigate further."
    })
    assert response.status_code == 200
    assert response.json()["status"] == "rejected"

def test_decision_cannot_be_changed_after_approval():
    created = create_request().json()
    approval_id = created["approval_id"]
    headers = {"X-Approval-Token": TOKEN}
    body = {"decided_by": "service-owner", "decision_reason": "Approved after review."}
    assert client.post(f"/api/v1/approvals/{approval_id}/approve", headers=headers, json=body).status_code == 200
    assert client.post(f"/api/v1/approvals/{approval_id}/reject", headers=headers, json=body).status_code == 409

def test_execution_is_blocked_even_after_approval():
    created = create_request().json()
    approval_id = created["approval_id"]
    headers = {"X-Approval-Token": TOKEN}
    body = {"decided_by": "service-owner", "decision_reason": "Approved after review."}
    client.post(f"/api/v1/approvals/{approval_id}/approve", headers=headers, json=body)
    response = client.post(f"/api/v1/approvals/{approval_id}/execute", headers=headers)
    assert response.status_code == 200
    assert response.json()["executed"] is False
    assert response.json()["status"] == "execution_disabled"

def test_unsupported_action_is_rejected():
    response = client.post("/api/v1/approvals", headers={"X-Approval-Token": TOKEN}, json={
        "action": "delete_everything", "target": "production",
        "reason": "This action should not be accepted.", "requested_by": "ops-engineer"
    })
    assert response.status_code == 422

def test_list_can_filter_pending_approvals():
    create_request()
    response = client.get("/api/v1/approvals?status=pending", headers={"X-Approval-Token": TOKEN})
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["status"] == "pending"
