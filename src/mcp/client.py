"""MCP client — connects to Pluggy MCP server via stdio transport.

Spawns the Pluggy MCP server (src.mcp.pluggy_server) as a subprocess
and communicates using the Model Context Protocol (MCP) over stdio.
All calls go through PluggyTools for security enforcement, sanitization,
and audit logging.
"""
from __future__ import annotations

import asyncio
import json
import logging
import sys
from contextlib import AsyncExitStack
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

_PROJECT_ROOT = str(Path(__file__).resolve().parent.parent.parent)


class _MCPBridge:
    """Adapter exposing MCP tool calls as regular sync methods.

    PluggyTools expects a raw client with get_transactions / get_balances /
    get_accounts methods.  This adapter bridges MCP tool calls to that
    interface.
    """

    def __init__(self, call_tool_fn) -> None:
        self._call = call_tool_fn

    def get_transactions(self, start_date: str, end_date: str) -> List[Dict]:
        return self._call("get_transactions", {"start_date": start_date, "end_date": end_date})

    def get_balances(self) -> List[Dict]:
        return self._call("get_balances", {})

    def get_accounts(self) -> List[Dict]:
        return self._call("get_accounts", {})


class MCPClient:
    """Unified client for Órbita financial data.

    Spawns the Pluggy MCP server as a subprocess (stdio transport) and
    routes all calls through PluggyTools for allowlist enforcement,
    output sanitization, and audit logging.
    """

    def __init__(self) -> None:
        self._loop = asyncio.new_event_loop()
        self._stack = AsyncExitStack()
        self._session = None

        # Start MCP server subprocess and initialise session
        self._loop.run_until_complete(self._connect())
        logger.info("MCPClient: connected to Pluggy MCP server via stdio")

        # Wrap MCP tool calls with the security layer
        bridge = _MCPBridge(self._call_tool_sync)
        from src.mcp.pluggy_tools import PluggyTools
        self._tools = PluggyTools(bridge)

    # ── lifecycle ──────────────────────────────────────────────────────────

    async def _connect(self) -> None:
        from mcp import ClientSession
        from mcp.client.stdio import StdioServerParameters, stdio_client

        server_params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "src.mcp.pluggy_server"],
            cwd=_PROJECT_ROOT,
        )

        read, write = await self._stack.enter_async_context(
            stdio_client(server_params)
        )
        self._session = await self._stack.enter_async_context(
            ClientSession(read, write)
        )
        await self._session.initialize()

    def close(self) -> None:
        """Shut down the MCP server subprocess."""
        try:
            self._loop.run_until_complete(self._stack.aclose())
        except Exception:
            logger.debug("Error during MCP client cleanup", exc_info=True)
        finally:
            try:
                self._loop.close()
            except Exception:
                pass

    def __del__(self) -> None:
        try:
            if not self._loop.is_closed():
                self.close()
        except Exception:
            pass

    # ── tool calls ─────────────────────────────────────────────────────────

    def _call_tool_sync(self, name: str, arguments: dict) -> Any:
        """Synchronous wrapper around the async MCP tool call."""
        return self._loop.run_until_complete(self._call_tool(name, arguments))

    async def _call_tool(self, name: str, arguments: dict) -> Any:
        """Call an MCP tool and deserialise the JSON response."""
        result = await self._session.call_tool(name, arguments=arguments)
        if result.isError:
            text = result.content[0].text if result.content else "Unknown MCP error"
            raise RuntimeError(f"MCP tool '{name}' failed: {text}")
        # FastMCP splits list results into one TextContent per item.
        # Reassemble them into a single list.
        items = []
        for content in result.content:
            if hasattr(content, "text"):
                parsed = json.loads(content.text)
                if isinstance(parsed, list):
                    items.extend(parsed)
                else:
                    items.append(parsed)
        return items

    # ── public interface (same as before) ──────────────────────────────────

    def get_transactions(self, start_date: str, end_date: str) -> List[Dict]:
        return self._tools.get_transactions(start_date, end_date)

    def get_balances(self) -> List[Dict]:
        return self._tools.get_balances()

    def get_accounts(self) -> List[Dict]:
        return self._tools.get_accounts()
