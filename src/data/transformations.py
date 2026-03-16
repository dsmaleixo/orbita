"""Pure data transformation functions — no framework dependencies."""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List

# ── Category mapping ─────────────────────────────────────────────────────────

CATEGORY_MAP = {
    "alimentacao": ["supermercado", "restaurante", "ifood", "lanche", "padaria", "mercado", "uber eats", "rappi"],
    "transporte": ["uber", "99taxi", "combustivel", "estacionamento", "metro", "onibus", "transporte", "pedágio"],
    "moradia": ["aluguel", "condominio", "luz", "agua", "gas", "internet", "telefone", "enel", "sabesp", "claro", "vivo", "tim"],
    "saude": ["farmacia", "medico", "hospital", "plano de saude", "academia", "drogaria", "smart fit"],
    "educacao": ["escola", "faculdade", "curso", "livro", "material escolar", "spotify", "netflix", "prime", "udemy"],
    "lazer": ["cinema", "teatro", "viagem", "hotel", "bar", "balada", "show", "jogo", "steam"],
    "vestuario": ["roupa", "calcado", "acessorio", "renner", "riachuelo", "nike", "netshoes"],
    "investimentos": ["tesouro", "cdb", "fundo", "corretora", "xp", "rico", "nuinvest", "inter invest"],
}

# Map Pluggy's English category names to our local keys
PLUGGY_CATEGORY_MAP: Dict[str, str] = {
    "groceries": "alimentacao",
    "eating out": "alimentacao",
    "food delivery": "alimentacao",
    "restaurants": "alimentacao",
    "transport": "transporte",
    "ride sharing": "transporte",
    "gas stations": "transporte",
    "parking": "transporte",
    "rent": "moradia",
    "utilities": "moradia",
    "digital services": "moradia",
    "telecom": "moradia",
    "health": "saude",
    "pharmacy": "saude",
    "fitness": "saude",
    "education": "educacao",
    "streaming": "educacao",
    "entertainment": "lazer",
    "travel": "lazer",
    "hotels": "lazer",
    "clothing": "vestuario",
    "shopping": "vestuario",
    "investments": "investimentos",
    "savings": "investimentos",
    "transfers": "outros",
    "transfer - pix": "outros",
    "same person transfer": "outros",
    "credit card payment": "outros",
    "tax on financial operations": "outros",
    "services": "outros",
    "donations": "outros",
}


def normalize_pluggy_category(pluggy_cat: str) -> str:
    """Map a Pluggy English category to a local category key."""
    return PLUGGY_CATEGORY_MAP.get(pluggy_cat.lower(), "")


def categorize(description: str, pluggy_category: str = "") -> str:
    """Classify a transaction into a spending category.

    Uses the Pluggy category first, then falls back to keyword matching.
    """
    if pluggy_category:
        mapped = normalize_pluggy_category(pluggy_category)
        if mapped:
            return mapped
    d = description.lower()
    for cat, keywords in CATEGORY_MAP.items():
        if any(k in d for k in keywords):
            return cat
    return "outros"


# ── Data transformations ─────────────────────────────────────────────────────

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

    today = datetime.today()
    result = []
    for i in range(months - 1, -1, -1):
        # Use proper month arithmetic instead of timedelta(days=i*30)
        year = today.year
        month = today.month - i
        while month <= 0:
            month += 12
            year -= 1
        key = f"{year:04d}-{month:02d}"
        d = datetime(year, month, 1)
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
