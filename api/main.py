"""Órbita FastAPI REST API — wraps the data layer and LangGraph agent."""
from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Ensure project root is on sys.path so `app.*` and `src.*` imports work.
_PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.config import settings
from src.data.transformations import (
    categorize,
    default_date_range,
    get_balance_history,
    get_category_totals,
    get_monthly_data,
    get_recurring,
    get_summary,
)

# The fetchers use @st.cache_data, so we import the underlying MCP client
# directly to avoid depending on a running Streamlit instance.
from src.mcp.client import MCPClient

_mcp: MCPClient | None = None


def _mcp_client() -> MCPClient:
    global _mcp
    if _mcp is None:
        _mcp = MCPClient(mock=settings.MCP_MOCK)
    return _mcp


def fetch_transactions(start_date: str, end_date: str) -> List[Dict]:
    txns = _mcp_client().get_transactions(start_date, end_date)
    for t in txns:
        if not t.get("category") or t["category"] in ("", "outros"):
            t["category"] = categorize(t.get("description", ""))
    return txns


def fetch_balances() -> List[Dict]:
    return _mcp_client().get_balances()


def fetch_accounts() -> List[Dict]:
    return _mcp_client().get_accounts()

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(title="Órbita API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Lazy LangGraph singleton
# ---------------------------------------------------------------------------

_graph_instance = None


def _get_graph():
    """Build the LangGraph agent on first use and cache it."""
    global _graph_instance
    if _graph_instance is None:
        from src.graph.builder import build_graph

        _graph_instance = build_graph()
    return _graph_instance


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    intent: Optional[str] = None
    response: str = ""
    citations: List[Dict[str, Any]] = []


class ConfigResponse(BaseModel):
    mcp_mock: bool
    ollama_model: str
    connected: bool


class SummaryResponse(BaseModel):
    income: float = 0.0
    expenses: float = 0.0
    net: float = 0.0
    count: int = 0


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _dates(
    start: Optional[str],
    end: Optional[str],
) -> tuple[str, str]:
    """Return explicit dates or fall back to current-month default."""
    if start and end:
        return start, end
    return default_date_range()


def _safe_txns(start: Optional[str], end: Optional[str]) -> List[Dict]:
    """Fetch transactions, swallowing exceptions."""
    s, e = _dates(start, end)
    try:
        return fetch_transactions(s, e)
    except Exception:
        logger.exception("Error fetching transactions")
        return []


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/api/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/api/config", response_model=ConfigResponse)
def config() -> ConfigResponse:
    connected = bool(settings.PLUGGY_ITEM_ID) and not settings.MCP_MOCK
    return ConfigResponse(
        mcp_mock=settings.MCP_MOCK,
        ollama_model=settings.OLLAMA_MODEL,
        connected=connected,
    )


@app.get("/api/transactions")
def transactions(
    start: Optional[str] = Query(None),
    end: Optional[str] = Query(None),
) -> List[Dict[str, Any]]:
    return _safe_txns(start, end)


@app.get("/api/balances")
def balances() -> List[Dict[str, Any]]:
    try:
        return fetch_balances()
    except Exception:
        logger.exception("Error fetching balances")
        return []


@app.get("/api/accounts")
def accounts() -> List[Dict[str, Any]]:
    try:
        return fetch_accounts()
    except Exception:
        logger.exception("Error fetching accounts")
        return []


@app.get("/api/summary", response_model=SummaryResponse)
def summary(
    start: Optional[str] = Query(None),
    end: Optional[str] = Query(None),
) -> SummaryResponse:
    txns = _safe_txns(start, end)
    data = get_summary(txns)
    return SummaryResponse(**data)


@app.get("/api/monthly")
def monthly(
    start: Optional[str] = Query(None),
    end: Optional[str] = Query(None),
    months: int = Query(6),
) -> List[Dict[str, Any]]:
    txns = _safe_txns(start, end)
    try:
        return get_monthly_data(txns, months=months)
    except Exception:
        logger.exception("Error computing monthly data")
        return []


@app.get("/api/categories")
def categories(
    start: Optional[str] = Query(None),
    end: Optional[str] = Query(None),
) -> Dict[str, float]:
    txns = _safe_txns(start, end)
    try:
        return get_category_totals(txns)
    except Exception:
        logger.exception("Error computing category totals")
        return {}


@app.get("/api/recurring")
def recurring(
    start: Optional[str] = Query(None),
    end: Optional[str] = Query(None),
) -> List[Dict[str, Any]]:
    txns = _safe_txns(start, end)
    try:
        return get_recurring(txns)
    except Exception:
        logger.exception("Error computing recurring transactions")
        return []


@app.get("/api/balance-history")
def balance_history(
    start: Optional[str] = Query(None),
    end: Optional[str] = Query(None),
) -> List[Dict[str, Any]]:
    txns = _safe_txns(start, end)
    try:
        initial = 0.0
        bals = fetch_balances()
        if bals:
            initial = sum(b.get("balance", 0) for b in bals)
        return get_balance_history(txns, initial_balance=initial)
    except Exception:
        logger.exception("Error computing balance history")
        return []


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    try:
        from src.graph.state import make_initial_state

        graph = _get_graph()
        result = graph.invoke(make_initial_state(user_query=req.message))
        return ChatResponse(
            intent=result.get("intent"),
            response=result.get("final_response", ""),
            citations=result.get("citations", []),
        )
    except Exception:
        logger.exception("Error in chat endpoint")
        return ChatResponse(
            intent=None,
            response="Desculpe, ocorreu um erro ao processar sua mensagem.",
            citations=[],
        )


# ---------------------------------------------------------------------------
# Entrypoint (for `python -m api.main` or `python api/main.py`)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api.main:app", host="0.0.0.0", port=8001, reload=True)
