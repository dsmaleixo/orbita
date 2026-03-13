"""Unit tests for the supervisor agent."""
from __future__ import annotations

from unittest.mock import patch

import pytest

from src.agents.supervisor import supervisor_node
from src.graph.state import make_initial_state


class TestSupervisorQA:
    def test_financial_literacy_question_classified_as_qa(self):
        """'O que é CDI?' should be classified as qa."""
        state = make_initial_state(user_query="O que é CDI?")
        with patch("src.agents.supervisor.ChatOllama") as mock_cls:
            mock_cls.return_value.invoke.return_value.content = "qa"
            result = supervisor_node(state)
        assert result["intent"] == "qa"

    def test_tesouro_direto_question_classified_as_qa(self):
        """Tesouro Direto question should be qa."""
        state = make_initial_state(user_query="Como funciona o Tesouro Direto?")
        with patch("src.agents.supervisor.ChatOllama") as mock_cls:
            mock_cls.return_value.invoke.return_value.content = "qa"
            result = supervisor_node(state)
        assert result["intent"] == "qa"

    def test_poupanca_question_classified_as_qa(self):
        """Poupança question should be qa."""
        state = make_initial_state(user_query="A poupança é um bom investimento?")
        with patch("src.agents.supervisor.ChatOllama") as mock_cls:
            mock_cls.return_value.invoke.return_value.content = "qa"
            result = supervisor_node(state)
        assert result["intent"] == "qa"


class TestSupervisorAutomation:
    def test_categorize_expenses_classified_as_automation(self):
        """'Categorize minhas despesas' should be classified as automation."""
        state = make_initial_state(user_query="Categorize minhas despesas do mês")
        result = supervisor_node(state)
        assert result["intent"] == "automation"

    def test_goal_check_classified_as_automation(self):
        """Goal-related query should be automation."""
        state = make_initial_state(user_query="Estou atingindo minhas metas financeiras?")
        result = supervisor_node(state)
        assert result["intent"] == "automation"

    def test_report_request_classified_as_automation(self):
        """Report request should be automation with report sub-type."""
        state = make_initial_state(user_query="Gerar relatório mensal das minhas finanças")
        result = supervisor_node(state)
        assert result["intent"] == "automation"
        assert result.get("automation_type") == "report"


class TestSupervisorRefuse:
    def test_investment_advice_classified_as_refuse(self):
        """'Qual ação devo comprar' should be classified as refuse."""
        state = make_initial_state(user_query="Qual ação devo comprar para ficar rico?")
        result = supervisor_node(state)
        assert result["intent"] == "refuse"

    def test_portfolio_allocation_classified_as_refuse(self):
        """Portfolio allocation request should be refuse."""
        state = make_initial_state(user_query="Devo colocar 60% em ações e 40% em renda fixa?")
        with patch("src.agents.supervisor.ChatOllama") as mock_cls:
            mock_cls.return_value.invoke.return_value.content = "refuse"
            result = supervisor_node(state)
        assert result["intent"] == "refuse"

    def test_llm_fallback_on_error(self):
        """If LLM raises exception, should default to qa."""
        state = make_initial_state(user_query="O que é inflação?")
        with patch("src.agents.supervisor.ChatOllama") as mock_cls:
            mock_cls.return_value.invoke.side_effect = Exception("Connection timeout")
            result = supervisor_node(state)
        assert result["intent"] == "qa"
