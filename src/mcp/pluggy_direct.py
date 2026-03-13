"""Direct Pluggy REST API client — no separate MCP server process required.

Used when MCP_MOCK=false. Calls api.pluggy.ai directly and adapts the
responses to the same interface as MockMCPServer so PluggyTools works
identically in both modes.
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)


class PluggyDirectClient:
    """Calls Pluggy's REST API directly, returning data in the same shape
    as MockMCPServer so the rest of the app is unaffected."""

    def __init__(self, client_id: str, client_secret: str, item_id: Optional[str] = None,
                 base_url: str = "https://api.pluggy.ai") -> None:
        if not client_id or not client_secret:
            raise ValueError(
                "PLUGGY_CLIENT_ID and PLUGGY_CLIENT_SECRET must be set in .env"
            )
        self._client_id = client_id
        self._client_secret = client_secret
        self._item_id = item_id or None  # None → auto-discover on first use
        self._http = httpx.Client(base_url=base_url, timeout=30.0)
        self._api_key: Optional[str] = None
        self._expires_at: Optional[datetime] = None

    def _auth_header(self) -> Dict[str, str]:
        now = datetime.now(timezone.utc)
        if not self._api_key or (self._expires_at and now >= self._expires_at):
            resp = self._http.post(
                "/auth",
                json={"clientId": self._client_id, "clientSecret": self._client_secret},
            )
            resp.raise_for_status()
            self._api_key = resp.json()["apiKey"]
            self._expires_at = now + timedelta(hours=1, minutes=45)
            logger.info("Pluggy: authenticated successfully")
        return {"X-API-KEY": self._api_key}

    def create_connect_token(self, client_user_id: str = "orbita-user") -> str:
        """Create a Pluggy Connect Token for the Connect Widget."""
        resp = self._http.post(
            "/connect_token",
            json={"clientUserId": client_user_id},
            headers=self._auth_header(),
        )
        resp.raise_for_status()
        return resp.json()["accessToken"]

    # ── Public interface (mirrors MockMCPServer) ───────────────────────────

    def get_transactions(self, start_date: str, end_date: str) -> List[Dict]:
        """Fetch all transactions across all accounts for the date range."""
        accounts = self._fetch_accounts()
        all_txns: List[Dict] = []
        for acc in accounts:
            page, total_pages = 1, 1
            while page <= total_pages:
                resp = self._http.get(
                    "/transactions",
                    params={"accountId": acc["id"], "from": start_date,
                            "to": end_date, "pageSize": 500, "page": page},
                    headers=self._auth_header(),
                )
                resp.raise_for_status()
                data = resp.json()
                for t in data.get("results", []):
                    all_txns.append({
                        "id": str(t.get("id", "")),
                        "date": str(t.get("date", ""))[:10],
                        "description": str(t.get("description", ""))[:200],
                        "amount": float(t.get("amount", 0)),
                        "type": str(t.get("type", "")),
                        "category": str(t.get("category", "")),
                        "account_id": str(acc["id"]),
                    })
                total_pages = data.get("totalPages", 1)
                page += 1
        all_txns.sort(key=lambda x: x["date"], reverse=True)
        logger.info("Pluggy: fetched %d transactions", len(all_txns))
        return all_txns

    def get_balances(self) -> List[Dict]:
        """Fetch current balances for all accounts."""
        accounts = self._fetch_accounts()
        return [
            {
                "account_id": str(a.get("id", "")),
                "account_type": str(a.get("type", "")).lower(),
                "institution": str(a.get("institution", {}).get("name", "")),
                "balance": float(a.get("balance", 0)),
                "currency": str(a.get("currencyCode", "BRL")),
            }
            for a in accounts
        ]

    def get_accounts(self) -> List[Dict]:
        """Fetch account metadata."""
        return [
            {
                "id": str(a.get("id", "")),
                "account_type": str(a.get("type", "")).lower(),
                "subtype": str(a.get("subtype", "")),
                "name": str(a.get("name", ""))[:100],
                "institution_name": str(a.get("institution", {}).get("name", ""))[:100],
                "currency_code": str(a.get("currencyCode", "BRL")),
            }
            for a in self._fetch_accounts()
        ]

    def _resolve_item_id(self) -> str:
        """Return configured item_id or raise a clear setup error."""
        if self._item_id:
            return self._item_id
        raise RuntimeError(
            "PLUGGY_ITEM_ID is not set. "
            "Go to the 'Conectar Banco' page in the app to create a connection, "
            "or set PLUGGY_ITEM_ID in .env."
        )

    def get_item_status(self) -> dict:
        """Retrieve the current sync status of the configured item."""
        resp = self._http.get(
            f"/items/{self._resolve_item_id()}",
            headers=self._auth_header(),
        )
        resp.raise_for_status()
        return resp.json()

    def _fetch_accounts(self) -> List[Dict]:
        resp = self._http.get(
            "/accounts",
            params={"itemId": self._resolve_item_id()},
            headers=self._auth_header(),
        )
        resp.raise_for_status()
        return resp.json().get("results", [])
