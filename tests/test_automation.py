"""Unit tests for the automation agent."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from src.agents.automation import (
    _categorize_transaction,
    _run_categorize,
    _run_goal_alert,
    _run_report,
    automation_node,
)
from src.graph.state import make_initial_state


class TestCategorizationLogic:
    def test_supermarket_categorized_as_alimentacao(self):
        assert _categorize_transaction("Supermercado Extra") == "alimentacao"

    def test_uber_categorized_as_transporte(self):
        assert _categorize_transaction("Uber Brasil") == "transporte"

    def test_rent_categorized_as_moradia(self):
        assert _categorize_transaction("Aluguel Ap Centro") == "moradia"

    def test_drugstore_categorized_as_saude(self):
        assert _categorize_transaction("Drogasil Farmácia") == "saude"

    def test_netflix_categorized_as_lazer_or_educacao(self):
        cat = _categorize_transaction("Netflix")
        assert cat in ("lazer", "educacao")

    def test_unknown_merchant_categorized_as_outros(self):
        assert _categorize_transaction("XYZ Unknown Store 12345") == "outros"


class TestRunCategorize:
    def test_categorize_returns_categories_dict(self, sample_transactions):
        result = _run_categorize(sample_transactions)
        assert "categories" in result
        assert "total_transactions" in result
        assert result["total_transactions"] == len(sample_transactions)

    def test_categorize_sums_amounts_correctly(self):
        txns = [
            {"description": "Supermercado", "amount": -100.0},
            {"description": "Supermercado", "amount": -50.0},
        ]
        result = _run_categorize(txns)
        assert result["categories"]["alimentacao"]["total"] == 150.0
        assert result["categories"]["alimentacao"]["count"] == 2

    def test_categorize_empty_transactions(self):
        result = _run_categorize([])
        assert result["categories"] == {}
        assert result["total_transactions"] == 0


class TestRunGoalAlert:
    def test_alert_when_savings_below_required(self):
        txns = [
            {"description": "Salário", "amount": 4500.0},
            {"description": "Aluguel", "amount": -2000.0},
            {"description": "Supermercado", "amount": -1500.0},
            {"description": "Outros", "amount": -800.0},
        ]
        goals = [{"name": "Reserva", "target_amount": 30000.0, "months_remaining": 3}]
        result = _run_goal_alert(txns, goals)
        # Required = 30000/3 = 10000/month; savings = 200 < 10000
        assert result["num_alerts"] > 0

    def test_no_alert_when_savings_sufficient(self):
        txns = [
            {"description": "Salário", "amount": 10000.0},
            {"description": "Aluguel", "amount": -1500.0},
        ]
        goals = [{"name": "Reserva", "target_amount": 10000.0, "months_remaining": 12}]
        result = _run_goal_alert(txns, goals)
        # Required = ~833/month; savings = 8500 >> 833
        assert result["num_alerts"] == 0


class TestAutomationNode:
    def test_categorize_node_returns_automation_output(self, patched_mcp_client):
        state = make_initial_state(
            user_query="Categorize despesas",
            intent="automation",
            automation_type="categorize",
        )
        with patch("src.mcp.client.MCPClient", return_value=patched_mcp_client):
            result = automation_node(state)
        assert "automation_output" in result
        assert result["automation_output"] is not None
        assert "final_response" in result

    def test_report_node_returns_report_output(self, patched_mcp_client):
        state = make_initial_state(
            user_query="Gerar relatório",
            intent="automation",
            automation_type="report",
        )
        with patch("src.mcp.client.MCPClient", return_value=patched_mcp_client):
            result = automation_node(state)
        assert result["automation_output"] is not None
        output = result["automation_output"]
        assert "summary" in output
        assert "insights" in output

    def test_automation_node_populates_mcp_tool_calls(self, patched_mcp_client):
        state = make_initial_state(
            user_query="Categorize despesas",
            intent="automation",
            automation_type="categorize",
        )
        with patch("src.mcp.client.MCPClient", return_value=patched_mcp_client):
            result = automation_node(state)
        assert len(result["mcp_tool_calls"]) >= 1
        assert result["mcp_tool_calls"][0]["tool"] == "get_transactions"

    def test_final_response_includes_disclaimer(self, patched_mcp_client):
        state = make_initial_state(
            user_query="Categorize despesas",
            intent="automation",
            automation_type="categorize",
        )
        with patch("src.mcp.client.MCPClient", return_value=patched_mcp_client):
            result = automation_node(state)
        assert "educacional" in result["final_response"].lower()
