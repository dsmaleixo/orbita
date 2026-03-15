"""Órbita FastAPI REST API — wraps the data layer and LangGraph agent."""
from __future__ import annotations

import logging
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Ensure project root is on sys.path so `app.*` and `src.*` imports work.
_PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from fastapi import FastAPI, HTTPException, Query
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

from src.mcp.client import MCPClient
from src.mcp.pluggy_direct import PluggyDirectClient

_mcp: MCPClient | None = None


def _mcp_client() -> MCPClient:
    global _mcp
    if _mcp is None:
        _mcp = MCPClient()
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
    ollama_model: str
    connected: bool
    item_ids: List[str] = []


class ConnectRequest(BaseModel):
    itemId: str


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
    ids = settings.pluggy_item_ids
    return ConfigResponse(
        ollama_model=settings.OLLAMA_MODEL,
        connected=len(ids) > 0,
        item_ids=ids,
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


def _update_env_var(key: str, value: str) -> None:
    """Update a variable in the .env file, or append it if missing."""
    env_path = Path(_PROJECT_ROOT) / ".env"
    if not env_path.exists():
        env_path.write_text(f"{key}={value}\n", encoding="utf-8")
        return
    text = env_path.read_text(encoding="utf-8")
    pattern = rf"^{re.escape(key)}=.*$"
    if re.search(pattern, text, flags=re.MULTILINE):
        text = re.sub(pattern, f"{key}={value}", text, flags=re.MULTILINE)
    else:
        text = text.rstrip("\n") + f"\n{key}={value}\n"
    env_path.write_text(text, encoding="utf-8")


@app.post("/api/connect-token")
def connect_token() -> Dict[str, str]:
    """Create a Pluggy Connect Token for the Connect Widget."""
    try:
        client = PluggyDirectClient(
            client_id=settings.PLUGGY_CLIENT_ID,
            client_secret=settings.PLUGGY_CLIENT_SECRET,
            base_url=settings.PLUGGY_BASE_URL,
        )
        token = client.create_connect_token()
        return {"accessToken": token}
    except Exception:
        logger.exception("Error creating connect token")
        raise HTTPException(status_code=500, detail="Falha ao criar token de conexão. Verifique as credenciais Pluggy.")


@app.post("/api/connect")
def connect(req: ConnectRequest) -> Dict[str, Any]:
    """Add a new Item ID from the Connect Widget."""
    global _mcp

    # Append to existing list (avoid duplicates)
    current_ids = settings.pluggy_item_ids
    if req.itemId not in current_ids:
        current_ids.append(req.itemId)

    new_value = ",".join(current_ids)
    settings.PLUGGY_ITEM_ID = new_value
    os.environ["PLUGGY_ITEM_ID"] = new_value
    if _mcp is not None:
        _mcp.close()
        _mcp = None
    _update_env_var("PLUGGY_ITEM_ID", new_value)

    logger.info("Connected Pluggy item: %s (total: %d)", req.itemId, len(current_ids))
    return {"status": "ok", "itemId": req.itemId, "item_ids": current_ids}


@app.delete("/api/connections/{item_id}")
def disconnect(item_id: str) -> Dict[str, Any]:
    """Remove a connected Item ID."""
    global _mcp

    current_ids = settings.pluggy_item_ids
    current_ids = [i for i in current_ids if i != item_id]

    new_value = ",".join(current_ids)
    settings.PLUGGY_ITEM_ID = new_value
    os.environ["PLUGGY_ITEM_ID"] = new_value
    if _mcp is not None:
        _mcp.close()
        _mcp = None
    _update_env_var("PLUGGY_ITEM_ID", new_value)

    logger.info("Disconnected Pluggy item: %s (remaining: %d)", item_id, len(current_ids))
    return {"status": "ok", "item_ids": current_ids}


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
