"""Shared fixtures for Órbita test suite."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import List
from unittest.mock import MagicMock, patch

import pytest
from langchain_core.documents import Document

from src.graph.state import make_initial_state


# ── Document / state fixtures ──────────────────────────────────────────────────

@pytest.fixture
def sample_docs() -> List[Document]:
    """10 synthetic financial education documents for testing."""
    return [
        Document(
            page_content="O Tesouro Selic acompanha a taxa básica de juros (Selic). "
                         "O investimento mínimo é de R$30,00. É indicado para reserva de emergência.",
            metadata={"title": "Tesouro Direto", "source_url": "https://tesourodireto.com.br", "page_number": 1, "source_id": "tesouro"},
        ),
        Document(
            page_content="A poupança rende 0,5% ao mês + TR quando a Selic está acima de 8,5% ao ano. "
                         "Tem cobertura do FGC de até R$250.000.",
            metadata={"title": "Poupança", "source_url": "https://bcb.gov.br/poupanca", "page_number": 1, "source_id": "poupanca"},
        ),
        Document(
            page_content="CDI é a taxa de referência para renda fixa, muito próxima da Selic. "
                         "CDB, LCI e LCA são remunerados como percentual do CDI.",
            metadata={"title": "CDI e Renda Fixa", "source_url": "https://bcb.gov.br/cdi", "page_number": 2, "source_id": "cdi"},
        ),
        Document(
            page_content="O FGTS é depositado mensalmente pelo empregador: 8% do salário. "
                         "Pode ser sacado em demissão sem justa causa ou aposentadoria.",
            metadata={"title": "FGTS", "source_url": "https://caixa.gov.br/fgts", "page_number": 1, "source_id": "fgts"},
        ),
        Document(
            page_content="O seguro-desemprego exige 12 meses de trabalho na 1ª solicitação, "
                         "9 meses na 2ª e 6 meses nas demais.",
            metadata={"title": "Seguro-Desemprego", "source_url": "https://gov.br/seguro", "page_number": 3, "source_id": "seguro"},
        ),
    ]


@pytest.fixture
def base_state():
    """Base OrbitaState for a simple Q&A query."""
    return make_initial_state(user_query="O que é o Tesouro Selic?")


@pytest.fixture
def automation_state():
    """Base OrbitaState for an automation query."""
    return make_initial_state(
        user_query="Categorize minhas despesas",
        intent="automation",
        automation_type="categorize",
    )


# ── Mock fixtures ──────────────────────────────────────────────────────────────

@pytest.fixture
def mock_vectorstore(sample_docs):
    """Mock VectorStore that returns sample_docs for any search query."""
    vs = MagicMock()
    vs.search.return_value = sample_docs
    vs.search_with_scores.return_value = [(doc, 0.9) for doc in sample_docs]
    vs.is_loaded = True
    return vs


@pytest.fixture
def mock_llm_qa():
    """Mock ChatOllama that returns a Q&A response."""
    mock = MagicMock()
    mock.invoke.return_value = MagicMock(
        content="O Tesouro Selic é um título público que acompanha a taxa Selic. "
                "[Fonte: Tesouro Direto, p.1] O investimento mínimo é de R$30,00."
    )
    return mock


@pytest.fixture
def mock_llm_supervisor_qa():
    """Mock ChatOllama that returns 'qa' classification."""
    mock = MagicMock()
    mock.invoke.return_value = MagicMock(content="qa")
    return mock


@pytest.fixture
def mock_llm_supervisor_automation():
    """Mock ChatOllama that returns 'automation' classification."""
    mock = MagicMock()
    mock.invoke.return_value = MagicMock(content="automation")
    return mock


@pytest.fixture
def mock_llm_supervisor_refuse():
    """Mock ChatOllama that returns 'refuse' classification."""
    mock = MagicMock()
    mock.invoke.return_value = MagicMock(content="refuse")
    return mock


@pytest.fixture
def mock_llm_self_check_pass():
    """Mock ChatOllama that returns self-check pass."""
    mock = MagicMock()
    mock.invoke.return_value = MagicMock(
        content='{"all_supported": true, "unsupported_claims": []}'
    )
    return mock


@pytest.fixture
def mock_llm_self_check_fail():
    """Mock ChatOllama that returns self-check fail."""
    mock = MagicMock()
    mock.invoke.return_value = MagicMock(
        content='{"all_supported": false, "unsupported_claims": ["Taxa específica não encontrada nos documentos"]}'
    )
    return mock


@pytest.fixture
def mock_mcp_transactions():
    """Synthetic transaction list for MCP mock testing."""
    return [
        {"id": "T001", "date": "2025-01-03", "description": "Supermercado Extra", "amount": -250.0},
        {"id": "T002", "date": "2025-01-05", "description": "Salário Empresa ABC", "amount": 4500.0},
        {"id": "T003", "date": "2025-01-07", "description": "Uber Brasil", "amount": -35.5},
        {"id": "T004", "date": "2025-01-10", "description": "Aluguel Ap", "amount": -1800.0},
        {"id": "T005", "date": "2025-01-22", "description": "Netflix", "amount": -44.9},
    ]


@pytest.fixture
def mock_mcp_client(mock_mcp_transactions):
    """Mock MCPClient that returns synthetic data."""
    client = MagicMock()
    client.get_transactions.return_value = mock_mcp_transactions
    client.get_balances.return_value = [
        {"account_id": "ACC001", "balance": 2847.50, "currency": "BRL"}
    ]
    client.get_accounts.return_value = [
        {"account_id": "ACC001", "account_type": "corrente", "status": "active"}
    ]
    return client


@pytest.fixture
def tmp_log_file(tmp_path):
    """Temporary log file path for audit log tests."""
    return tmp_path / "mcp_audit_test.log"


@pytest.fixture
def tmp_allowlist_file(tmp_path):
    """Temporary allowlist YAML for security tests."""
    import yaml
    allowlist = {
        "allowed_tools": ["get_transactions", "get_balances", "get_accounts"],
        "prohibited_operations": ["delete_account", "create_payment"],
    }
    path = tmp_path / "test_allowlist.yaml"
    with open(path, "w") as f:
        yaml.dump(allowlist, f)
    return path
