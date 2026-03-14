"""Pluggy MCP Server — wraps Pluggy Open Finance REST API as MCP tools.

This is the custom MCP server (Bonus B2) that exposes Pluggy's financial data
as standardized MCP tools consumable by any MCP-compatible client.

Usage (stdio transport, default):
    python -m src.mcp.pluggy_server

Usage (SSE transport for HTTP clients):
    python -m src.mcp.pluggy_server --transport sse --port 8000

Environment variables required:
    PLUGGY_CLIENT_ID      — Pluggy API client ID
    PLUGGY_CLIENT_SECRET  — Pluggy API client secret
    PLUGGY_ITEM_ID        — Pluggy item ID (bank connection)
    PLUGGY_BASE_URL       — Pluggy API base URL (default: https://api.pluggy.ai)

Pluggy API docs: https://docs.pluggy.ai/
"""
from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import httpx
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)

# ── Pluggy REST API client ─────────────────────────────────────────────────────

PLUGGY_BASE_URL = os.getenv("PLUGGY_BASE_URL", "https://api.pluggy.ai")
PLUGGY_CLIENT_ID = os.getenv("PLUGGY_CLIENT_ID", "")
PLUGGY_CLIENT_SECRET = os.getenv("PLUGGY_CLIENT_SECRET", "")
PLUGGY_ITEM_ID = os.getenv("PLUGGY_ITEM_ID", "")


class PluggyAPIClient:
    """Thin REST client for Pluggy's Open Finance API."""

    def __init__(self) -> None:
        self._api_key: Optional[str] = None
        self._api_key_expires_at: Optional[datetime] = None
        self._http = httpx.Client(base_url=PLUGGY_BASE_URL, timeout=30.0)

    def _authenticate(self) -> str:
        """Obtain or refresh the Pluggy API key (JWT, valid ~2h)."""
        now = datetime.now(timezone.utc)
        if self._api_key and self._api_key_expires_at and now < self._api_key_expires_at:
            return self._api_key

        logger.info("Authenticating with Pluggy API...")
        response = self._http.post(
            "/auth",
            json={"clientId": PLUGGY_CLIENT_ID, "clientSecret": PLUGGY_CLIENT_SECRET},
        )
        response.raise_for_status()
        data = response.json()
        self._api_key = data["apiKey"]
        # Pluggy API keys expire in 2 hours; refresh after 1h45m to be safe
        self._api_key_expires_at = now + timedelta(hours=1, minutes=45)
        logger.info("Pluggy authentication successful.")
        return self._api_key

    def _headers(self) -> Dict[str, str]:
        return {"X-API-KEY": self._authenticate(), "Content-Type": "application/json"}

    def get_accounts(self, item_id: str) -> List[Dict]:
        """Fetch accounts linked to the given item (bank connection)."""
        response = self._http.get(
            "/accounts",
            params={"itemId": item_id},
            headers=self._headers(),
        )
        response.raise_for_status()
        data = response.json()
        return data.get("results", [])

    def get_transactions(
        self,
        account_id: str,
        start_date: str,
        end_date: str,
        page_size: int = 100,
    ) -> List[Dict]:
        """Fetch transactions for a given account and date range.

        Pluggy paginates results; this method fetches all pages.
        """
        all_transactions: List[Dict] = []
        page = 1

        while True:
            response = self._http.get(
                "/transactions",
                params={
                    "accountId": account_id,
                    "from": start_date,
                    "to": end_date,
                    "pageSize": page_size,
                    "page": page,
                },
                headers=self._headers(),
            )
            response.raise_for_status()
            data = response.json()
            results = data.get("results", [])
            all_transactions.extend(results)

            total_pages = data.get("totalPages", 1)
            if page >= total_pages:
                break
            page += 1

        return all_transactions

    def get_identity(self, item_id: str) -> Dict:
        """Fetch identity information for a connected item."""
        response = self._http.get(
            "/identity",
            params={"itemId": item_id},
            headers=self._headers(),
        )
        response.raise_for_status()
        return response.json()


# ── MCP Server setup ───────────────────────────────────────────────────────────

mcp = FastMCP(
    name="pluggy-orbita",
    instructions=(
        "Pluggy Open Finance MCP server for Órbita. "
        "Provides read-only access to Brazilian bank transactions, balances, and accounts. "
        "Only get_transactions, get_balances, and get_accounts are exposed. "
        "No write operations are permitted."
    ),
)

_pluggy_client: Optional[PluggyAPIClient] = None


def _get_pluggy_client() -> PluggyAPIClient:
    """Return a module-level Pluggy API client singleton."""
    global _pluggy_client
    if _pluggy_client is None:
        if not PLUGGY_CLIENT_ID or not PLUGGY_CLIENT_SECRET:
            raise ValueError(
                "PLUGGY_CLIENT_ID and PLUGGY_CLIENT_SECRET must be set in .env."
            )
        _pluggy_client = PluggyAPIClient()
    return _pluggy_client


def _sanitize_transaction(txn: Dict) -> Dict:
    """Return only the fields needed by the Órbita agents (no PII)."""
    return {
        "id": str(txn.get("id", "")),
        "date": str(txn.get("date", ""))[:10],  # YYYY-MM-DD
        "description": str(txn.get("description", ""))[:200],
        "amount": float(txn.get("amount", 0)),
        "type": str(txn.get("type", "")),
        "category": str(txn.get("category", "")),
        "account_id": str(txn.get("accountId", "")),
    }


def _sanitize_account(acc: Dict) -> Dict:
    """Return only non-PII account fields."""
    return {
        "id": str(acc.get("id", "")),
        "type": str(acc.get("type", "")),
        "subtype": str(acc.get("subtype", "")),
        "name": str(acc.get("name", ""))[:100],
        "balance": float(acc.get("balance", 0)),
        "currency_code": str(acc.get("currencyCode", "BRL")),
    }


# ── MCP Tools ──────────────────────────────────────────────────────────────────

@mcp.tool()
def get_transactions(start_date: str, end_date: str) -> List[Dict]:
    """Fetch bank transactions from Pluggy Open Finance for the given date range.

    Args:
        start_date: Start date in ISO format (YYYY-MM-DD), e.g. '2025-01-01'
        end_date: End date in ISO format (YYYY-MM-DD), e.g. '2025-01-31'

    Returns:
        List of transactions with: id, date, description, amount (BRL), type, category
    """
    client = _get_pluggy_client()
    item_id = PLUGGY_ITEM_ID

    # Get all accounts for this item
    accounts = client.get_accounts(item_id)
    if not accounts:
        return []

    all_transactions: List[Dict] = []
    for account in accounts:
        account_id = account.get("id", "")
        if not account_id:
            continue
        txns = client.get_transactions(account_id, start_date, end_date)
        for txn in txns:
            sanitized = _sanitize_transaction(txn)
            all_transactions.append(sanitized)

    # Sort by date descending
    all_transactions.sort(key=lambda x: x.get("date", ""), reverse=True)
    logger.info(
        "get_transactions(%s, %s): returned %d transactions",
        start_date, end_date, len(all_transactions),
    )
    return all_transactions


@mcp.tool()
def get_balances() -> List[Dict]:
    """Fetch current account balances from Pluggy Open Finance.

    Returns:
        List of accounts with: id, type, subtype, name, balance (BRL), currency_code
    """
    client = _get_pluggy_client()
    item_id = PLUGGY_ITEM_ID
    accounts = client.get_accounts(item_id)
    result = [_sanitize_account(acc) for acc in accounts]
    logger.info("get_balances(): returned %d accounts", len(result))
    return result


@mcp.tool()
def get_accounts() -> List[Dict]:
    """Fetch metadata for all linked bank accounts from Pluggy Open Finance.

    Returns:
        List of account metadata: id, type, subtype, name, currency_code
    """
    client = _get_pluggy_client()
    item_id = PLUGGY_ITEM_ID
    accounts = client.get_accounts(item_id)
    result = []
    for acc in accounts:
        result.append({
            "id": str(acc.get("id", "")),
            "type": str(acc.get("type", "")),
            "subtype": str(acc.get("subtype", "")),
            "name": str(acc.get("name", ""))[:100],
            "currency_code": str(acc.get("currencyCode", "BRL")),
            "institution_name": str(acc.get("institution", {}).get("name", ""))[:100],
        })
    logger.info("get_accounts(): returned %d accounts", len(result))
    return result


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    parser = argparse.ArgumentParser(description="Pluggy MCP Server for Órbita")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default="stdio",
        help="MCP transport type (default: stdio)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for SSE transport (default: 8000)",
    )
    args = parser.parse_args()

    if not PLUGGY_CLIENT_ID or not PLUGGY_CLIENT_SECRET:
        print(
            "WARNING: PLUGGY_CLIENT_ID and PLUGGY_CLIENT_SECRET are not set.\n"
            "The server will start but tool calls will fail.\n"
            "Set these in your .env file or environment.",
            file=sys.stderr,
        )

    if args.transport == "sse":
        print(f"Starting Pluggy MCP Server on http://0.0.0.0:{args.port}/sse")
        mcp.run(transport="sse")
    else:
        print("Starting Pluggy MCP Server (stdio transport)", file=sys.stderr)
        mcp.run(transport="stdio")
