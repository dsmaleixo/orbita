"""Tool definitions for Pluggy Open Finance MCP integration.

Each tool sanitizes output before returning to agent to prevent prompt injection.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List

from src.mcp.security import audit_log, enforce_allowlist, sanitize_mcp_output

logger = logging.getLogger(__name__)


class PluggyTools:
    """Wrappers for Pluggy MCP tools with security enforcement."""

    def __init__(self, raw_client: Any) -> None:
        """
        Args:
            raw_client: The underlying MCP transport (real or mock).
        """
        self._client = raw_client

    def get_transactions(self, start_date: str, end_date: str) -> List[Dict]:
        """Fetch transactions for the given date range.

        Args:
            start_date: ISO date string (YYYY-MM-DD)
            end_date: ISO date string (YYYY-MM-DD)

        Returns:
            List of sanitized transaction dicts.

        Raises:
            PermissionError: If tool is not in allowlist.
        """
        enforce_allowlist("get_transactions")
        logger.info("Fetching transactions: %s to %s", start_date, end_date)

        raw = self._client.get_transactions(start_date, end_date)
        sanitized = sanitize_mcp_output(raw)

        audit_log(
            tool_name="get_transactions",
            params={"start_date": start_date, "end_date": end_date},
            response_summary=f"record_count={len(sanitized)}",
        )

        return sanitized

    def get_balances(self) -> List[Dict]:
        """Fetch current account balances.

        Returns:
            List of sanitized balance dicts.

        Raises:
            PermissionError: If tool is not in allowlist.
        """
        enforce_allowlist("get_balances")
        logger.info("Fetching account balances")

        raw = self._client.get_balances()
        sanitized = sanitize_mcp_output(raw)

        audit_log(
            tool_name="get_balances",
            params={},
            response_summary=f"record_count={len(sanitized)}",
        )

        return sanitized

    def get_accounts(self) -> List[Dict]:
        """Fetch account metadata.

        Returns:
            List of sanitized account dicts.

        Raises:
            PermissionError: If tool is not in allowlist.
        """
        enforce_allowlist("get_accounts")
        logger.info("Fetching account metadata")

        raw = self._client.get_accounts()
        sanitized = sanitize_mcp_output(raw)

        audit_log(
            tool_name="get_accounts",
            params={},
            response_summary=f"record_count={len(sanitized)}",
        )

        return sanitized
