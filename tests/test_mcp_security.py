"""Unit tests for the MCP security layer."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from src.mcp.security import audit_log, enforce_allowlist, sanitize_mcp_output


class TestAllowlistEnforcement:
    def test_allowlisted_tool_does_not_raise(self, tmp_allowlist_file):
        """get_transactions is in allowlist — should not raise."""
        with patch("src.mcp.security.settings") as mock_settings:
            mock_settings.mcp_allowlist_path = tmp_allowlist_file
            # Should not raise
            enforce_allowlist("get_transactions")

    def test_allowlisted_get_balances_does_not_raise(self, tmp_allowlist_file):
        """get_balances is in allowlist — should not raise."""
        with patch("src.mcp.security.settings") as mock_settings:
            mock_settings.mcp_allowlist_path = tmp_allowlist_file
            mock_settings.audit_log_path = tmp_allowlist_file.parent / "audit.log"
            enforce_allowlist("get_balances")

    def test_non_allowlisted_tool_raises_permission_error(self, tmp_allowlist_file, tmp_log_file):
        """delete_account is NOT in allowlist — must raise PermissionError."""
        with patch("src.mcp.security.settings") as mock_settings:
            mock_settings.mcp_allowlist_path = tmp_allowlist_file
            mock_settings.audit_log_path = tmp_log_file
            with pytest.raises(PermissionError) as exc_info:
                enforce_allowlist("delete_account")
        assert "delete_account" in str(exc_info.value)
        assert "not in the allowlist" in str(exc_info.value)

    def test_unknown_tool_raises_permission_error(self, tmp_allowlist_file, tmp_log_file):
        """Any unknown tool must raise PermissionError."""
        with patch("src.mcp.security.settings") as mock_settings:
            mock_settings.mcp_allowlist_path = tmp_allowlist_file
            mock_settings.audit_log_path = tmp_log_file
            with pytest.raises(PermissionError):
                enforce_allowlist("create_payment")


class TestAuditLog:
    def test_audit_log_entry_written(self, tmp_log_file):
        """Calling audit_log should write a JSON entry to the log file."""
        with patch("src.mcp.security.settings") as mock_settings:
            mock_settings.audit_log_path = tmp_log_file
            audit_log(
                tool_name="get_transactions",
                params={"start_date": "2025-01-01", "end_date": "2025-01-31"},
                response_summary="record_count=5",
            )
        assert tmp_log_file.exists()
        lines = tmp_log_file.read_text().strip().split("\n")
        assert len(lines) == 1
        entry = json.loads(lines[0])
        assert entry["tool"] == "get_transactions"
        assert entry["response_summary"] == "record_count=5"
        assert "timestamp" in entry

    def test_audit_log_does_not_contain_financial_amounts(self, tmp_log_file):
        """Financial amounts must be redacted in audit log."""
        with patch("src.mcp.security.settings") as mock_settings:
            mock_settings.audit_log_path = tmp_log_file
            audit_log(
                tool_name="get_balances",
                params={"amount": 5000.0, "account_number": "12345-6"},
                response_summary="record_count=2",
            )
        entry = json.loads(tmp_log_file.read_text().strip())
        assert entry["params"]["amount"] == "[REDACTED]"
        assert entry["params"]["account_number"] == "[REDACTED]"

    def test_blocked_tool_logged_as_blocked(self, tmp_log_file):
        """Blocked tool call should have blocked=True in log entry."""
        with patch("src.mcp.security.settings") as mock_settings:
            mock_settings.audit_log_path = tmp_log_file
            audit_log(
                tool_name="delete_account",
                params={},
                response_summary="BLOCKED: tool not in allowlist",
                blocked=True,
            )
        entry = json.loads(tmp_log_file.read_text().strip())
        assert entry["blocked"] is True

    def test_multiple_entries_appended(self, tmp_log_file):
        """Multiple audit_log calls should append separate lines."""
        with patch("src.mcp.security.settings") as mock_settings:
            mock_settings.audit_log_path = tmp_log_file
            for i in range(3):
                audit_log(
                    tool_name="get_transactions",
                    params={"start_date": f"2025-0{i+1}-01"},
                    response_summary=f"record_count={i}",
                )
        lines = tmp_log_file.read_text().strip().split("\n")
        assert len(lines) == 3


class TestSanitizeMCPOutput:
    def test_control_chars_stripped(self):
        """Control characters should be removed from strings."""
        dirty = "Normal text\x00\x07\x1b[dangerous]"
        result = sanitize_mcp_output(dirty)
        assert "\x00" not in result
        assert "\x07" not in result
        assert "\x1b" not in result

    def test_long_string_truncated(self):
        """Strings longer than max_field_length should be truncated."""
        long_str = "A" * 300
        result = sanitize_mcp_output(long_str, max_field_length=256)
        assert len(result) <= 256 + 3  # +3 for "..."
        assert result.endswith("...")

    def test_dict_sanitized_recursively(self):
        """Dicts should be sanitized recursively."""
        data = {"name": "Normal", "description": "Text\x00Injection"}
        result = sanitize_mcp_output(data)
        assert "\x00" not in result["description"]

    def test_list_sanitized_recursively(self):
        """Lists should be sanitized recursively."""
        data = ["OK", "Injection\x07Attack"]
        result = sanitize_mcp_output(data)
        assert "\x07" not in result[1]

    def test_numbers_pass_through(self):
        """Numeric values should pass through unchanged."""
        assert sanitize_mcp_output(42) == 42
        assert sanitize_mcp_output(3.14) == 3.14

    def test_none_passes_through(self):
        """None should pass through unchanged."""
        assert sanitize_mcp_output(None) is None
