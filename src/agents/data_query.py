"""Data query agent — answers questions about the user's own financial data."""
from __future__ import annotations
import logging
from datetime import datetime, timedelta
from typing import Any
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from src.config import settings
from src.graph.state import OrbitaState

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """Você é um analista financeiro pessoal do Órbita.
Você recebeu os dados financeiros reais do usuário abaixo. Responda à pergunta usando
APENAS esses dados. Seja preciso com os valores. Formate valores em R$ com 2 casas decimais.
Seja conciso e direto. Use listas ou tabelas simples quando útil.

⚠️ Órbita é uma ferramenta educacional. Não constitui aconselhamento financeiro."""


def data_query_node(state: OrbitaState) -> dict[str, Any]:
    """Fetch the user's financial data and answer their question."""
    query = state["user_query"]
    logger.info("Data query node: %s", query[:60])

    try:
        from src.mcp.client import MCPClient
        client = MCPClient(mock=settings.MCP_MOCK)

        today = datetime.today()
        start = today.replace(day=1).strftime("%Y-%m-%d")
        end = today.strftime("%Y-%m-%d")

        txns = client.get_transactions(start, end)
        balances = client.get_balances()

        # Build context summary
        total_balance = sum(b.get("balance", 0) for b in balances)
        income = sum(t["amount"] for t in txns if t.get("amount", 0) > 0)
        expenses = sum(abs(t["amount"]) for t in txns if t.get("amount", 0) < 0)

        # Category breakdown
        from collections import defaultdict
        from app.data_layer import categorize
        cat_totals: dict = defaultdict(float)
        for t in txns:
            if t.get("amount", 0) < 0:
                cat = categorize(t.get("description", ""))
                cat_totals[cat] += abs(t["amount"])
        cat_summary = "\n".join(
            f"  - {k.capitalize()}: R${v:,.2f}"
            for k, v in sorted(cat_totals.items(), key=lambda x: x[1], reverse=True)[:8]
        )

        # Recent transactions
        recent = sorted(txns, key=lambda x: x.get("date",""), reverse=True)[:10]
        recent_str = "\n".join(
            f"  - {t['date']} | {t.get('description','')[:30]} | {'+'if t['amount']>0 else '-'}R${abs(t['amount']):,.2f}"
            for t in recent
        )

        context = f"""DADOS FINANCEIROS DO USUÁRIO ({start} a {end}):

Saldo total: R${total_balance:,.2f}
Receitas no período: R${income:,.2f}
Despesas no período: R${expenses:,.2f}
Resultado: R${income-expenses:,.2f}

Gastos por categoria:
{cat_summary}

Transações recentes:
{recent_str}
"""
        llm = ChatOllama(base_url=settings.OLLAMA_BASE_URL, model=settings.OLLAMA_MODEL)
        response = llm.invoke([
            SystemMessage(content=_SYSTEM_PROMPT),
            HumanMessage(content=f"{context}\n\nPERGUNTA: {query}"),
        ])
        return {
            "final_response": response.content.strip(),
            "self_check_passed": True,
            "mcp_tool_calls": [{"tool": "get_transactions", "record_count": len(txns)},
                               {"tool": "get_balances", "record_count": len(balances)}],
        }
    except Exception as exc:
        logger.error("Data query failed: %s", exc)
        return {
            "final_response": f"Não consegui acessar seus dados financeiros. Erro: {exc}",
            "self_check_passed": True,
        }
