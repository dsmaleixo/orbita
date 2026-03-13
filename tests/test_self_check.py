"""Unit tests for the self-check agent."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from langchain_core.documents import Document

from src.agents.self_check import self_check_node
from src.graph.state import make_initial_state


def _make_state_with_docs(draft: str, docs: list, attempts: int = 1) -> dict:
    state = make_initial_state(user_query="O que é o Tesouro Selic?")
    state["draft_response"] = draft
    state["retrieved_docs"] = docs
    state["retrieval_attempts"] = attempts
    return state


_GROUNDED_DRAFT = (
    "O Tesouro Selic é um título público que acompanha a taxa Selic. "
    "[Fonte: Tesouro Direto, p.1]"
)

_UNGROUNDED_DRAFT = (
    "A taxa de retorno exata do Tesouro Selic para 2025 será de 13,75% ao ano, "
    "conforme previsão proprietária do mercado."
)


class TestSelfCheckPass:
    def test_grounded_response_passes(self, sample_docs):
        """Response supported by retrieved docs should pass self-check."""
        state = _make_state_with_docs(_GROUNDED_DRAFT, sample_docs, attempts=1)
        with patch("src.agents.self_check.ChatOllama") as mock_cls:
            mock_cls.return_value.invoke.return_value.content = (
                '{"all_supported": true, "unsupported_claims": []}'
            )
            result = self_check_node(state)
        assert result["self_check_passed"] is True
        assert result["unsupported_claims"] == []
        assert result["final_response"] == _GROUNDED_DRAFT

    def test_passes_sets_final_response(self, sample_docs):
        """When self_check passes, final_response equals draft_response."""
        state = _make_state_with_docs(_GROUNDED_DRAFT, sample_docs, attempts=1)
        with patch("src.agents.self_check.ChatOllama") as mock_cls:
            mock_cls.return_value.invoke.return_value.content = (
                '{"all_supported": true, "unsupported_claims": []}'
            )
            result = self_check_node(state)
        assert result["final_response"] == _GROUNDED_DRAFT


class TestSelfCheckFailRetry:
    def test_ungrounded_response_fails_with_retry_available(self, sample_docs):
        """Ungrounded response with attempts < MAX should signal retry (not refuse)."""
        state = _make_state_with_docs(_UNGROUNDED_DRAFT, sample_docs, attempts=1)
        with patch("src.agents.self_check.ChatOllama") as mock_cls:
            mock_cls.return_value.invoke.return_value.content = (
                '{"all_supported": false, "unsupported_claims": ["taxa 13.75% não encontrada"]}'
            )
            result = self_check_node(state)
        assert result["self_check_passed"] is False
        assert len(result["unsupported_claims"]) > 0
        # Should NOT set a final refusal response (empty string → triggers retry in graph)
        assert result["final_response"] == ""

    def test_unsupported_claims_populated(self, sample_docs):
        """unsupported_claims should be populated on failure."""
        state = _make_state_with_docs(_UNGROUNDED_DRAFT, sample_docs, attempts=1)
        with patch("src.agents.self_check.ChatOllama") as mock_cls:
            mock_cls.return_value.invoke.return_value.content = (
                '{"all_supported": false, "unsupported_claims": ["claim A", "claim B"]}'
            )
            result = self_check_node(state)
        assert "claim A" in result["unsupported_claims"]


class TestSelfCheckRefusalOnMaxRetries:
    def test_max_retries_triggers_refusal(self, sample_docs):
        """After MAX_RETRIEVAL_ATTEMPTS retries, must issue refusal."""
        state = _make_state_with_docs(_UNGROUNDED_DRAFT, sample_docs, attempts=2)
        with patch("src.agents.self_check.ChatOllama") as mock_cls:
            mock_cls.return_value.invoke.return_value.content = (
                '{"all_supported": false, "unsupported_claims": ["claim não suportada"]}'
            )
            result = self_check_node(state)
        assert result["self_check_passed"] is False
        assert result["final_response"] != ""
        assert "evidências" in result["final_response"].lower() or "aconselhamento" in result["final_response"].lower()

    def test_no_draft_triggers_refusal(self):
        """Empty draft response should trigger immediate refusal."""
        state = make_initial_state(user_query="Pergunta qualquer")
        state["draft_response"] = ""
        state["retrieved_docs"] = []
        result = self_check_node(state)
        assert result["self_check_passed"] is False
        assert result["final_response"] != ""
