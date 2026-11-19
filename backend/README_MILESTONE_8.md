# OpsPilot AI — Milestone 8

Milestone 8 adds a persistent, token-protected human approval workflow for remediation proposals. It records requests, decisions and audit events in SQLite. **No infrastructure actions are executed in this milestone**, even after approval. AWS/GCP credentials are not required; demo mode remains supported.

## What's new

- Persistent SQLite approval queue with pending, approved and rejected states.
- Shared-secret protection using the `X-Approval-Token` header and constant-time comparison.
- Allowlisted remediation actions: restart instance, stop instance, resize instance and scale service.
- Immutable decision transition: pending requests can be approved or rejected once.
- Audit trail for request and decision events.
- Explicit execution endpoint that always returns `execution_disabled` and `executed: false`.
- MCP tool `create_remediation_approval` for agents to create a persistent proposal.

## Important security boundary

The shared token is a local-development gate, not a production identity system. The `requested_by` and `decided_by` values are audit labels supplied by the caller and are not verified identities. Before production use, replace this with SSO/OIDC/JWT-based authentication, role-based authorization, per-user audit identity, approval separation-of-duties, rate limiting, secret management and a reviewed change-management policy. Do not expose this API publicly with a shared development token.

No AWS/GCP write permissions or execution adapters are implemented. Approving a request only records a decision; it does not restart, stop, resize or scale any resource.

## Setup

Preserve your Milestone 7 `backend/.env` and `backend/data/qdrant` folder. Add a unique local approval token to `backend/.env`:

```env
APPROVAL_API_TOKEN=replace-with-a-long-random-local-secret
APPROVAL_DB_PATH=./data/approvals.db
```

Keep `.env` out of Git. The SQLite database is stored under `backend/data/` and should also be excluded from Git.

Install and test:

```bash
cd backend
source .venv/bin/activate
pip install -r requirements.txt
pytest -v
```

Expected: 38 tests (30 previous + 8 approval workflow tests).

## Run services

Terminal 1:

```bash
cd backend
source .venv/bin/activate
python -m app.mcp_server.server
```

Terminal 2:

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

Swagger: http://127.0.0.1:8000/docs

## API examples

All approval endpoints require `X-Approval-Token`.

Create a request with `POST /api/v1/approvals`:

```json
{
  "action": "restart_instance",
  "target": "i-demo-001",
  "reason": "Sustained high CPU requires service-owner review.",
  "requested_by": "ops-engineer"
}
```

Approve using `POST /api/v1/approvals/{approval_id}/approve`:

```json
{
  "decided_by": "service-owner",
  "decision_reason": "Reviewed evidence; approved for the next change window."
}
```

Other endpoints: `GET /api/v1/approvals`, `GET /api/v1/approvals/{approval_id}`, `GET /api/v1/approvals/{approval_id}/audit`, `POST /api/v1/approvals/{approval_id}/reject`, and `POST /api/v1/approvals/{approval_id}/execute`. The execute endpoint is a safety stop and never performs a cloud operation.
