"""MCP client — Pluggy direct API or mock.

  MCP_MOCK=true   → MockMCPServer  (synthetic data, no credentials)
  MCP_MOCK=false  → PluggyDirectClient  (real Pluggy REST API)

No separate server process needed in either mode.
"""
from __future__ import annotations

import logging
from typing import Dict, List, Optional

from src.config import settings

logger = logging.getLogger(__name__)


class MCPClient:
    """Unified client for Órbita financial data.

    All calls go through PluggyTools for allowlist enforcement,
    output sanitization, and audit logging.
    """

    def __init__(self, mock: Optional[bool] = None) -> None:
        use_mock = mock if mock is not None else settings.MCP_MOCK

        if use_mock:
            from src.mcp.mock_server import MockMCPServer
            raw = MockMCPServer()
            logger.info("MCPClient: mock mode (synthetic data)")
        else:
            from src.mcp.pluggy_direct import PluggyDirectClient
            raw = PluggyDirectClient(
                client_id=settings.PLUGGY_CLIENT_ID,
                client_secret=settings.PLUGGY_CLIENT_SECRET,
                item_id=settings.PLUGGY_ITEM_ID or None,
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
