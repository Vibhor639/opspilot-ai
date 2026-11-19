"""Persistent human-approval workflow. It records decisions but never changes infrastructure."""
from __future__ import annotations
import json
import sqlite3
from contextlib import contextmanager
import uuid
from datetime import datetime, timezone
from pathlib import Path
from app.core.config import settings

ALLOWED_ACTIONS = {"restart_instance", "stop_instance", "resize_instance", "scale_service"}

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _connect() -> sqlite3.Connection:
    path = Path(settings.APPROVAL_DB_PATH).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path), timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

@contextmanager
def _db():
    conn = _connect()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def initialize_store() -> None:
    with _db() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS approvals (
            approval_id TEXT PRIMARY KEY, action TEXT NOT NULL, target TEXT NOT NULL,
            reason TEXT NOT NULL, requested_by TEXT NOT NULL, status TEXT NOT NULL,
            created_at TEXT NOT NULL, decided_by TEXT, decision_reason TEXT, decided_at TEXT,
            executed INTEGER NOT NULL DEFAULT 0 CHECK (executed IN (0,1))
        )""")
        conn.execute("""CREATE TABLE IF NOT EXISTS approval_audit (
            event_id INTEGER PRIMARY KEY AUTOINCREMENT, approval_id TEXT NOT NULL,
            event_type TEXT NOT NULL, actor TEXT NOT NULL, details TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(approval_id) REFERENCES approvals(approval_id)
        )""")

def _record(row: sqlite3.Row) -> dict:
    result = dict(row)
    result["executed"] = bool(result["executed"])
    return result

def create_approval(action: str, target: str, reason: str, requested_by: str) -> dict:
    if action not in ALLOWED_ACTIONS:
        raise ValueError("Unsupported remediation action.")
    if not target.strip() or not reason.strip() or not requested_by.strip():
        raise ValueError("Target, reason and requester are required.")
    initialize_store()
    approval_id, created_at = str(uuid.uuid4()), _now()
    with _db() as conn:
        conn.execute(
            "INSERT INTO approvals (approval_id, action, target, reason, requested_by, status, created_at) VALUES (?,?,?,?,?,?,?)",
            (approval_id, action, target.strip(), reason.strip(), requested_by.strip(), "pending", created_at),
        )
        conn.execute(
            "INSERT INTO approval_audit (approval_id,event_type,actor,details,created_at) VALUES (?,?,?,?,?)",
            (approval_id, "requested", requested_by.strip(), json.dumps({"action": action, "target": target.strip()}), created_at),
        )
    return get_approval(approval_id)

def list_approvals(status: str | None = None) -> list[dict]:
    initialize_store()
    with _db() as conn:
        if status:
            rows = conn.execute("SELECT * FROM approvals WHERE status=? ORDER BY created_at DESC", (status,)).fetchall()
        else:
            rows = conn.execute("SELECT * FROM approvals ORDER BY created_at DESC").fetchall()
    return [_record(row) for row in rows]

def get_approval(approval_id: str) -> dict | None:
    initialize_store()
    with _db() as conn:
        row = conn.execute("SELECT * FROM approvals WHERE approval_id=?", (approval_id,)).fetchone()
    return _record(row) if row else None

def get_audit_events(approval_id: str) -> list[dict] | None:
    initialize_store()
    with _db() as conn:
        exists = conn.execute("SELECT 1 FROM approvals WHERE approval_id=?", (approval_id,)).fetchone()
        if not exists:
            return None
        rows = conn.execute("SELECT * FROM approval_audit WHERE approval_id=? ORDER BY event_id", (approval_id,)).fetchall()
    return [dict(row) for row in rows]

def decide_approval(approval_id: str, decision: str, decided_by: str, decision_reason: str) -> dict | None:
    if decision not in {"approved", "rejected"}:
        raise ValueError("Decision must be approved or rejected.")
    initialize_store()
    now = _now()
    with _db() as conn:
        conn.execute("BEGIN IMMEDIATE")
        row = conn.execute("SELECT * FROM approvals WHERE approval_id=?", (approval_id,)).fetchone()
        if not row:
            return None
        if row["status"] != "pending":
            raise RuntimeError(f"Approval is already {row['status']}.")
        conn.execute(
            "UPDATE approvals SET status=?, decided_by=?, decision_reason=?, decided_at=? WHERE approval_id=? AND status='pending'",
            (decision, decided_by.strip(), decision_reason.strip(), now, approval_id),
        )
        conn.execute(
            "INSERT INTO approval_audit (approval_id,event_type,actor,details,created_at) VALUES (?,?,?,?,?)",
            (approval_id, decision, decided_by.strip(), json.dumps({"reason": decision_reason.strip(), "executed": False}), now),
        )
    return get_approval(approval_id)

def record_execution_blocked(approval_id: str, actor: str = "system") -> None:
    now = _now()
    with _db() as conn:
        conn.execute(
            "INSERT INTO approval_audit (approval_id,event_type,actor,details,created_at) VALUES (?,?,?,?,?)",
            (approval_id, "execution_blocked", actor, json.dumps({"executed": False, "policy": "disabled"}), now),
        )
