"""Centralized configuration management for Órbita."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load .env from project root (two levels up from src/)
_project_root = Path(__file__).parent.parent
load_dotenv(_project_root / ".env", override=False)


class Settings:
    """Application settings loaded from environment variables."""

    # LLM
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.1:8b")

    # Embeddings
    EMBED_MODEL: str = os.getenv("EMBED_MODEL", "BAAI/bge-m3")
    RERANKER_MODEL: str = os.getenv("RERANKER_MODEL", "BAAI/bge-reranker-v2-m3")
    ENABLE_RERANKER: bool = os.getenv("ENABLE_RERANKER", "false").lower() == "true"

    # FAISS
    FAISS_INDEX_PATH: str = os.getenv("FAISS_INDEX_PATH", "data/faiss_index")

    # MCP
    MCP_SERVER_URL: str = os.getenv("MCP_SERVER_URL", "http://localhost:8000")
    MCP_ALLOWLIST_PATH: str = os.getenv("MCP_ALLOWLIST_PATH", "config/mcp_allowlist.yaml")

    # Pluggy credentials
    PLUGGY_CLIENT_ID: str = os.getenv("PLUGGY_CLIENT_ID", "")
    PLUGGY_CLIENT_SECRET: str = os.getenv("PLUGGY_CLIENT_SECRET", "")
    PLUGGY_ITEM_ID: str = os.getenv("PLUGGY_ITEM_ID", "")
    PLUGGY_BASE_URL: str = os.getenv("PLUGGY_BASE_URL", "https://api.pluggy.ai")

    # Logging
    AUDIT_LOG_PATH: str = os.getenv("AUDIT_LOG_PATH", "logs/mcp_audit.log")
    LANGGRAPH_VERBOSE: bool = os.getenv("LANGGRAPH_VERBOSE", "0") == "1"

    # Safety
    MAX_RETRIEVAL_ATTEMPTS: int = int(os.getenv("MAX_RETRIEVAL_ATTEMPTS", "2"))
    SELF_CHECK_THRESHOLD: float = float(os.getenv("SELF_CHECK_THRESHOLD", "0.5"))

    @property
    def pluggy_item_ids(self) -> list[str]:
        """Return PLUGGY_ITEM_ID as a list (comma-separated in .env)."""
        raw = self.PLUGGY_ITEM_ID
        if not raw:
            return []
        return [item_id.strip() for item_id in raw.split(",") if item_id.strip()]

    @property
    def faiss_index_path(self) -> Path:
        return _project_root / self.FAISS_INDEX_PATH

    @property
    def audit_log_path(self) -> Path:
        path = _project_root / self.AUDIT_LOG_PATH
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def mcp_allowlist_path(self) -> Path:
        return _project_root / self.MCP_ALLOWLIST_PATH


settings = Settings()


if __name__ == "__main__":
    print(f"OLLAMA_MODEL: {settings.OLLAMA_MODEL}")
    print(f"EMBED_MODEL: {settings.EMBED_MODEL}")
    print(f"FAISS_INDEX_PATH: {settings.faiss_index_path}")
    print(f"PLUGGY_BASE_URL: {settings.PLUGGY_BASE_URL}")
