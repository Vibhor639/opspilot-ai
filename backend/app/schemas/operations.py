from typing import Literal
from pydantic import BaseModel, Field

Provider = Literal["AWS", "GCP"]
Environment = Literal["production", "staging", "development"]
Severity = Literal["low", "medium", "high", "critical"]
IncidentStatus = Literal["open", "investigating", "resolved"]
UtilizationClass = Literal["underutilized", "healthy", "overutilized"]

class Asset(BaseModel):
    id: str
    name: str
    provider: Provider
    resource_type: str
    region: str
    monthly_cost: float = Field(ge=0)
    previous_monthly_cost: float = Field(ge=0)
    cpu_utilization_percent: float = Field(ge=0, le=100)
    memory_utilization_percent: float = Field(ge=0, le=100)
    environment: Environment
    owner_team: str
    tags: dict[str, str] = Field(default_factory=dict)

class CostService(BaseModel):
    service: str
    current_month: float
    previous_month: float
    change_amount: float
    change_percent: float

class CostSummary(BaseModel):
    currency: str
    current_month: float
    previous_month: float
    change_amount: float
    change_percent: float
    services: list[CostService]

class CostAnomaly(BaseModel):
    service: str
    current_month: float
    previous_month: float
    change_amount: float
    change_percent: float
    severity: Literal["medium", "high"]
    explanation: str

class Incident(BaseModel):
    id: str
    title: str
    severity: Severity
    status: IncidentStatus
    affected_asset_ids: list[str]

class UtilizationItem(BaseModel):
    asset_id: str
    asset_name: str
    resource_type: str
    cpu_utilization_percent: float
    memory_utilization_percent: float
    classification: UtilizationClass
    recommendation: str

class UtilizationReport(BaseModel):
    total_assets: int
    underutilized: int
    healthy: int
    overutilized: int
    items: list[UtilizationItem]

class InvestigationRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)

class InvestigationFinding(BaseModel):
    title: str
    detail: str
    evidence: list[str]

class InvestigationResponse(BaseModel):
    investigation_id: str
    question: str
    summary: str
    findings: list[InvestigationFinding]
    recommended_actions: list[str]
    requires_human_approval: bool = True
    mode: str = "deterministic_demo"
    disclaimer: str

class DocumentRecord(BaseModel):
    document_id: str
    filename: str
    file_type: str
    chunk_count: int
    status: str = "indexed"

class RAGQueryRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=10)

class RAGSource(BaseModel):
    citation: str
    document_id: str
    filename: str
    page_number: int | None = None
    chunk_id: str
    score: float
    text: str

class RAGQueryResponse(BaseModel):
    question: str
    answer: str
    sources: list[RAGSource]
    retrieval_mode: str
    generation_mode: str
    warning: str | None = None


class MCPToolCallRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    arguments: dict = Field(default_factory=dict)
