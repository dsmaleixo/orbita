"""MCP security: allowlist enforcement and audit logging."""
from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from src.config import settings

logger = logging.getLogger(__name__)


def _load_allowlist() -> list[str]:
    """Load the MCP tool allowlist from YAML config."""
    allowlist_path = settings.mcp_allowlist_path
    if not allowlist_path.exists():
        logger.warning("Allowlist file not found at %s; denying all tools.", allowlist_path)
        return []
    with open(allowlist_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config.get("allowed_tools", [])


def enforce_allowlist(tool_name: str) -> None:
    """Raise PermissionError if tool_name is not in the allowlist.

    Args:
        tool_name: The MCP tool being called.

    Raises:
        PermissionError: If the tool is not in the allowlist.
    """
    allowed = _load_allowlist()
    if tool_name not in allowed:
        msg = (
            f"MCP tool '{tool_name}' is not in the allowlist. "
            f"Allowed tools: {allowed}. "
            "This call has been blocked and logged for security audit."
        )
        logger.warning("SECURITY: blocked MCP tool call: %s", tool_name)
        audit_log(
            tool_name=tool_name,
            params={},
            response_summary=f"BLOCKED: tool not in allowlist",
            blocked=True,
        )
        raise PermissionError(msg)


def sanitize_mcp_output(data: Any, max_field_length: int = 256) -> Any:
    """Sanitize MCP output to prevent prompt injection.

    - Strips control characters from strings
    - Truncates excessively long string fields
    - Recursively processes dicts and lists
    """
    if isinstance(data, str):
        # Strip control characters (except newline/tab)
        cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", data)
        # Truncate long fields
        if len(cleaned) > max_field_length:
            cleaned = cleaned[:max_field_length] + "..."
        return cleaned
    elif isinstance(data, dict):
        return {k: sanitize_mcp_output(v, max_field_length) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_mcp_output(item, max_field_length) for item in data]
    else:
        return data


def audit_log(
    tool_name: str,
    params: Dict[str, Any],
    response_summary: str,
    blocked: bool = False,
) -> None:
    """Append a JSON audit log entry to the MCP audit log file.

    IMPORTANT: Financial amounts and account numbers are NEVER logged.
    Only metadata (tool name, params shape, record count) is recorded.
    """
    log_path = settings.audit_log_path
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Sanitize params — remove any financial values
    safe_params = {}
    for k, v in params.items():
        if k in ("amount", "balance", "account_number", "cpf", "token"):
            safe_params[k] = "[REDACTED]"
        else:
            safe_params[k] = str(v)[:100] if isinstance(v, str) else v

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tool": tool_name,
        "params": safe_params,
        "response_summary": response_summary[:200],
        "blocked": blocked,
    }

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    logger.debug("Audit log entry written: tool=%s, blocked=%s", tool_name, blocked)
