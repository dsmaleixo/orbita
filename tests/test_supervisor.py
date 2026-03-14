"""Unit tests for the supervisor agent."""
from __future__ import annotations

from unittest.mock import patch

import pytest

from src.agents.supervisor import supervisor_node
from src.graph.state import make_initial_state


class TestSupervisorRAG:
    def test_financial_literacy_question_classified_as_rag(self):
        """'O que é CDI?' should be classified as rag (keyword match)."""
        state = make_initial_state(user_query="O que é CDI?")
        result = supervisor_node(state)
        assert result["intent"] == "rag"

    def test_tesouro_direto_question_classified_as_rag(self):
        """Tesouro Direto question should be rag (keyword match)."""
        state = make_initial_state(user_query="Como funciona o Tesouro Direto?")
        result = supervisor_node(state)
        assert result["intent"] == "rag"

    def test_poupanca_question_classified_as_rag(self):
        """Poupança question should be rag (keyword match)."""
        state = make_initial_state(user_query="A poupança é um bom investimento?")
        result = supervisor_node(state)
        assert result["intent"] == "rag"


class TestSupervisorData:
    def test_categorize_expenses_classified_as_data(self):
        """'Categorize minhas despesas' should be classified as data."""
        state = make_initial_state(user_query="Categorize minhas despesas do mês")
        result = supervisor_node(state)
        assert result["intent"] == "data"

    def test_goal_check_classified_as_data(self):
        """Goal-related query about personal finances should be data."""
        state = make_initial_state(user_query="Estou atingindo minhas metas financeiras?")
        result = supervisor_node(state)
        assert result["intent"] == "data"

    def test_report_request_classified_as_data(self):
        """Report request should be classified as data."""
        state = make_initial_state(user_query="Gerar relatório mensal das minhas finanças")
        result = supervisor_node(state)
        assert result["intent"] == "data"


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
        """If LLM raises exception for ambiguous query, should default to general."""
        state = make_initial_state(user_query="Me ajude com algo")
        with patch("src.agents.supervisor.ChatOllama") as mock_cls:
            mock_cls.return_value.invoke.side_effect = Exception("Connection timeout")
            result = supervisor_node(state)
        assert result["intent"] == "general"
