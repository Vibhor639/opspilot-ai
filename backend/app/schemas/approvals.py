from typing import Literal
from pydantic import BaseModel, Field

RemediationAction = Literal["restart_instance", "stop_instance", "resize_instance", "scale_service"]
ApprovalStatus = Literal["pending", "approved", "rejected"]

class ApprovalCreateRequest(BaseModel):
    action: RemediationAction
    target: str = Field(min_length=1, max_length=200)
    reason: str = Field(min_length=10, max_length=2000)
    requested_by: str = Field(min_length=2, max_length=120)

class ApprovalDecisionRequest(BaseModel):
    decided_by: str = Field(min_length=2, max_length=120)
    decision_reason: str = Field(min_length=3, max_length=1000)

class ApprovalRecord(BaseModel):
    approval_id: str
    action: RemediationAction
    target: str
    reason: str
    requested_by: str
    status: ApprovalStatus
    created_at: str
    decided_by: str | None = None
    decision_reason: str | None = None
    decided_at: str | None = None
    executed: bool = False

class ApprovalAuditEvent(BaseModel):
    event_id: int
    approval_id: str
    event_type: str
    actor: str
    details: str
    created_at: str
