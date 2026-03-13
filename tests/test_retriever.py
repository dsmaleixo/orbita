"""Unit tests for the retriever agent."""
from __future__ import annotations

from unittest.mock import patch

import pytest
from langchain_core.documents import Document

from src.agents.retriever import retriever_node
from src.graph.state import make_initial_state


class TestRetrieverBasic:
    def test_retriever_returns_documents(self, sample_docs, mock_vectorstore):
        """Retriever should return documents from FAISS."""
        state = make_initial_state(user_query="O que é o Tesouro Selic?")
        with patch("src.agents.retriever.get_vectorstore", return_value=mock_vectorstore):
            result = retriever_node(state)
        assert "retrieved_docs" in result
        assert len(result["retrieved_docs"]) > 0

    def test_retriever_returns_docs_with_metadata(self, sample_docs, mock_vectorstore):
        """Retrieved documents should have required metadata fields."""
        state = make_initial_state(user_query="Como funciona a poupança?")
        with patch("src.agents.retriever.get_vectorstore", return_value=mock_vectorstore):
            result = retriever_node(state)
        docs = result["retrieved_docs"]
        for doc in docs:
            assert "title" in doc.metadata
            assert "source_url" in doc.metadata
            assert "page_number" in doc.metadata

    def test_retriever_increments_attempts(self, mock_vectorstore):
        """retrieval_attempts should increment on each call."""
        state = make_initial_state(user_query="O que é CDI?")
        assert state["retrieval_attempts"] == 0
        with patch("src.agents.retriever.get_vectorstore", return_value=mock_vectorstore):
            result = retriever_node(state)
        assert result["retrieval_attempts"] == 1

        # Second call (simulate retry)
        state2 = dict(state)
        state2["retrieval_attempts"] = result["retrieval_attempts"]
        with patch("src.agents.retriever.get_vectorstore", return_value=mock_vectorstore):
            result2 = retriever_node(state2)
        assert result2["retrieval_attempts"] == 2

    def test_retriever_empty_index_returns_empty(self):
        """If FAISS index doesn't exist, retriever should return empty list gracefully."""
        from unittest.mock import MagicMock
        empty_vs = MagicMock()
        empty_vs.search.return_value = []
        state = make_initial_state(user_query="Pergunta qualquer")
        with patch("src.agents.retriever.get_vectorstore", return_value=empty_vs):
            result = retriever_node(state)
        assert result["retrieved_docs"] == []
        assert result["retrieval_attempts"] == 1

    def test_retriever_calls_vectorstore_with_query(self, mock_vectorstore):
        """Retriever should pass the user_query to vectorstore.search."""
        query = "Como funciona o FGTS?"
        state = make_initial_state(user_query=query)
        with patch("src.agents.retriever.get_vectorstore", return_value=mock_vectorstore):
            retriever_node(state)
        mock_vectorstore.search.assert_called_once_with(query, k=5)
