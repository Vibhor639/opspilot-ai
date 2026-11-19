import os
from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "OpsPilot AI")
    APP_ENV: str = os.getenv("APP_ENV", "local")
    API_V1_PREFIX: str = os.getenv("API_V1_PREFIX", "/api/v1")
    QDRANT_PATH: str = os.getenv("QDRANT_PATH", "./data/qdrant")
    QDRANT_COLLECTION: str = os.getenv("QDRANT_COLLECTION", "opspilot_documents")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    AGENT_REASONING_MODE: str = os.getenv("AGENT_REASONING_MODE", "deterministic")
    MAX_UPLOAD_MB: int = int(os.getenv("MAX_UPLOAD_MB", "10"))
    MCP_SERVER_URL: str = os.getenv("MCP_SERVER_URL", "http://127.0.0.1:8001/mcp")
    CLOUD_MODE: str = os.getenv("CLOUD_MODE", "demo")
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    GCP_PROJECT_ID: str = os.getenv("GCP_PROJECT_ID", "")
    MCP_HOST: str = os.getenv("MCP_HOST", "127.0.0.1")
    MCP_PORT: int = int(os.getenv("MCP_PORT", "8001"))
    APPROVAL_API_TOKEN: str = os.getenv("APPROVAL_API_TOKEN", "")
    APPROVAL_DB_PATH: str = os.getenv("APPROVAL_DB_PATH", "./data/approvals.db")

settings = Settings()
