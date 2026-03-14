"""MCP client — Pluggy direct API.

Calls the Pluggy Open Finance REST API via PluggyDirectClient.
All calls go through PluggyTools for security enforcement, sanitization,
and audit logging.
"""
from __future__ import annotations

import logging
from typing import Dict, List

from src.config import settings

logger = logging.getLogger(__name__)


class MCPClient:
    """Unified client for Órbita financial data.

    All calls go through PluggyTools for allowlist enforcement,
    output sanitization, and audit logging.
    """

    def __init__(self) -> None:
        from src.mcp.pluggy_direct import PluggyDirectClient
        raw = PluggyDirectClient(
            client_id=settings.PLUGGY_CLIENT_ID,
            client_secret=settings.PLUGGY_CLIENT_SECRET,
            item_ids=settings.pluggy_item_ids,
            base_url=settings.PLUGGY_BASE_URL,
        )
        logger.info("MCPClient: Pluggy direct API")

        from src.mcp.pluggy_tools import PluggyTools
        self._tools = PluggyTools(raw)

    def get_transactions(self, start_date: str, end_date: str) -> List[Dict]:
        return self._tools.get_transactions(start_date, end_date)

    def get_balances(self) -> List[Dict]:
        return self._tools.get_balances()

    def get_accounts(self) -> List[Dict]:
        return self._tools.get_accounts()
