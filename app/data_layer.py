"""Centralized data layer — fetches and caches Pluggy data for all dashboard pages."""
from __future__ import annotations

import logging
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import streamlit as st

logger = logging.getLogger(__name__)

# ── Category mapping (same as automation agent) ────────────────────────────────

_CATEGORY_MAP = {
    "alimentacao": ["supermercado", "restaurante", "ifood", "lanche", "padaria", "mercado", "uber eats", "rappi"],
    "transporte": ["uber", "99taxi", "combustivel", "estacionamento", "metro", "onibus", "transporte", "pedágio"],
    "moradia": ["aluguel", "condominio", "luz", "agua", "gas", "internet", "telefone", "enel", "sabesp", "claro", "vivo", "tim"],
    "saude": ["farmacia", "medico", "hospital", "plano de saude", "academia", "drogaria", "smart fit"],
    "educacao": ["escola", "faculdade", "curso", "livro", "material escolar", "spotify", "netflix", "prime", "udemy"],
    "lazer": ["cinema", "teatro", "viagem", "hotel", "bar", "balada", "show", "jogo", "steam"],
    "vestuario": ["roupa", "calcado", "acessorio", "renner", "riachuelo", "nike", "netshoes"],
    "investimentos": ["tesouro", "cdb", "fundo", "corretora", "xp", "rico", "nuinvest", "inter invest"],
}


def categorize(description: str) -> str:
    d = description.lower()
    for cat, keywords in _CATEGORY_MAP.items():
        if any(k in d for k in keywords):
            return cat
    return "outros"


# ── Cached data fetchers ──────────────────────────────────────────────────────

def _pluggy_setup_warning() -> None:
    """Show a one-time Pluggy setup banner (stored in session_state to avoid flicker)."""
    if st.session_state.get("_pluggy_warn_shown"):
        return
    st.session_state["_pluggy_warn_shown"] = True
    st.warning(
        "**Conexão Pluggy não encontrada.**  \n"
        "Para usar dados reais:  \n"
        "1. Acesse [dashboard.pluggy.ai](https://dashboard.pluggy.ai)  \n"
        "2. Crie uma conexão usando o conector **Pluggy Bank** (login: `user_good`, senha: `password_good`)  \n"
        "3. Copie o **Item ID** gerado  \n"
        "4. Cole em `.env` → `PLUGGY_ITEM_ID=<o_id>`  \n"
        "5. Reinicie o app  \n\n"
        "Enquanto isso o app exibe dados vazios.",
        icon="⚠️",
    )


@st.cache_data(ttl=300, show_spinner=False)
def fetch_transactions(start_date: str, end_date: str) -> List[Dict]:
    """Fetch and enrich transactions from MCP (cached 5 min)."""
    from src.config import settings
    from src.mcp.client import MCPClient
    try:
        client = MCPClient(mock=settings.MCP_MOCK)
        txns = client.get_transactions(start_date, end_date)
    except Exception as exc:
        logger.warning("fetch_transactions failed: %s", exc)
        _pluggy_setup_warning()
        return []
    for t in txns:
        if not t.get("category") or t["category"] in ("", "outros"):
            t["category"] = categorize(t.get("description", ""))
    return txns


@st.cache_data(ttl=300, show_spinner=False)
def fetch_balances() -> List[Dict]:
    """Fetch account balances from MCP (cached 5 min)."""
    from src.config import settings
    from src.mcp.client import MCPClient
    try:
        client = MCPClient(mock=settings.MCP_MOCK)
        return client.get_balances()
    except Exception as exc:
        logger.warning("fetch_balances failed: %s", exc)
        return []


@st.cache_data(ttl=300, show_spinner=False)
def fetch_accounts() -> List[Dict]:
    """Fetch account metadata from MCP (cached 5 min)."""
    from src.config import settings
    from src.mcp.client import MCPClient
    try:
        client = MCPClient(mock=settings.MCP_MOCK)
        return client.get_accounts()
    except Exception as exc:
        logger.warning("fetch_accounts failed: %s", exc)
        return []


# ── Data transformations ──────────────────────────────────────────────────────

def get_summary(txns: List[Dict]) -> Dict:
    """Compute income, expenses, net for a list of transactions."""
    income = sum(t["amount"] for t in txns if t.get("amount", 0) > 0)
    expenses = sum(abs(t["amount"]) for t in txns if t.get("amount", 0) < 0)
    return {
        "income": income,
        "expenses": expenses,
        "net": income - expenses,
        "count": len(txns),
    }


def get_monthly_data(txns: List[Dict], months: int = 6) -> List[Dict]:
    """Aggregate transactions by month into income/expense groups."""
    monthly: Dict[str, Dict] = defaultdict(lambda: {"income": 0.0, "expenses": 0.0})
    for t in txns:
        key = t.get("date", "")[:7]  # YYYY-MM
        if t.get("amount", 0) > 0:
            monthly[key]["income"] += t["amount"]
        else:
            monthly[key]["expenses"] += abs(t["amount"])

    # Ensure last `months` months are present even if empty
    today = datetime.today()
    result = []
    for i in range(months - 1, -1, -1):
        d = today - timedelta(days=i * 30)
        key = d.strftime("%Y-%m")
        label = d.strftime("%b/%y")
        result.append({
            "month": label,
            "key": key,
            "income": monthly[key]["income"],
            "expenses": monthly[key]["expenses"],
            "net": monthly[key]["income"] - monthly[key]["expenses"],
        })
    return result


def get_category_totals(txns: List[Dict]) -> Dict[str, float]:
    """Sum expense amounts by category."""
    totals: Dict[str, float] = defaultdict(float)
    for t in txns:
        if t.get("amount", 0) < 0:
            cat = t.get("category", "outros")
            totals[cat] += abs(t["amount"])
    return dict(sorted(totals.items(), key=lambda x: x[1], reverse=True))


def get_recurring(txns: List[Dict]) -> List[Dict]:
    """Detect recurring transactions (same description, multiple months)."""
    by_desc: Dict[str, List] = defaultdict(list)
    for t in txns:
        if t.get("amount", 0) < 0:
            by_desc[t.get("description", "")].append(t)

    recurring = []
    for desc, entries in by_desc.items():
        months = set(e["date"][:7] for e in entries)
        if len(months) >= 2:
            avg = sum(abs(e["amount"]) for e in entries) / len(entries)
            latest = max(e["date"] for e in entries)
            recurring.append({
                "description": desc,
                "avg_amount": avg,
                "occurrences": len(entries),
                "months": len(months),
                "last_date": latest,
                "category": entries[0].get("category", "outros"),
            })

    return sorted(recurring, key=lambda x: x["avg_amount"], reverse=True)


def get_balance_history(txns: List[Dict], initial_balance: float = 0) -> List[Dict]:
    """Build a cumulative balance history from transactions."""
    sorted_txns = sorted(txns, key=lambda x: x.get("date", ""))
    history = []
    running = initial_balance
    for t in sorted_txns:
        running += t.get("amount", 0)
        history.append({"date": t.get("date", ""), "balance": running})
    return history


def default_date_range() -> tuple[str, str]:
    """Return start/end dates for the current month."""
    today = datetime.today()
    start = today.replace(day=1).strftime("%Y-%m-%d")
    end = today.strftime("%Y-%m-%d")
    return start, end
