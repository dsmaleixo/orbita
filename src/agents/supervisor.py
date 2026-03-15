"""Supervisor agent — routes to general | rag | data | refuse."""
from __future__ import annotations
import logging
from typing import Any
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from src.config import settings
from src.graph.state import OrbitaState

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """Você é o roteador do assistente financeiro Órbita.
Classifique a mensagem do usuário em UMA das quatro categorias:

- "general": saudações, perguntas gerais, conversas casuais, perguntas que não precisam de documentos
  Exemplos: "Olá", "Como você funciona?", "Me conte uma curiosidade"

- "rag": perguntas sobre educação financeira, conceitos, filosofia de finanças pessoais, conteúdo de livros
  como Rich Dad Poor Dad, O Homem Mais Rico da Babilônia, O Investidor Inteligente, etc.
  Exemplos: "O que é fluxo de caixa?", "Como o livro Pai Rico explica ativos?", "O que é investir com inteligência?"

- "data": perguntas sobre os dados financeiros PESSOAIS do usuário — gastos, saldo, transações, metas
  Exemplos: "Quanto gastei esse mês?", "Qual meu saldo?", "Quais são minhas maiores despesas?"

- "refuse": pedidos de recomendação específica de investimento, conselho de carteira personalizado
  Exemplos: "Qual ação comprar?", "Monte minha carteira de investimentos"

Responda APENAS com uma palavra: general, rag, data, ou refuse."""

_RAG_KEYWORDS = [
    # Books and authors
    "pai rico", "rich dad", "babilônia", "homem mais rico", "investidor inteligente",
    "kiyosaki", "clason", "graham", "buffett", "ray dalio", "thiago nigro",
    "kahneman", "duhigg", "poder do hábito", "rápido e devagar",
    "livro", "filosofia", "mentalidade", "princípios",
    # Financial concepts
    "hábito financeiro", "liberdade financeira", "independência financeira",
    "ativo", "passivo", "fluxo de caixa", "juros compostos", "juros simples",
    "inflação", "taxa selic", "taxa de juros", "amortização",
    "o que é", "como funciona", "explique", "educação financeira", "conceito",
    "poupança", "investimento", "tesouro direto", "cdi", "fgts", "renda fixa",
    "renda variável", "fundo", "ações", "dividendos", "carteira",
    "planejamento financeiro", "orçamento", "endividamento", "dívida",
    # Open Finance / Banking
    "open finance", "open banking", "sistema financeiro", "banco central",
    "bacen", "cvm", "direitos do consumidor", "cidadania financeira",
    # Behavioral finance
    "viés cognitivo", "psicologia financeira", "tomada de decisão",
    "consumo consciente", "finanças pessoais",
]
_DATA_KEYWORDS = [
    "meu saldo", "minha conta", "minhas despesas", "meus gastos", "gastei",
    "quanto ganhei", "minha renda", "minhas transações", "meu extrato",
    "quanto tenho", "onde gastei", "categoria", "esse mês", "semana passada",
    "relatório", "resumo financeiro", "minhas finanças",
]
_REFUSE_PATTERNS = [
    "qual ação comprar", "qual fundo comprar", "me dê conselho de investimento",
    "monte minha carteira", "devo colocar", "melhor ação", "recomenda",
]


def supervisor_node(state: OrbitaState) -> dict[str, Any]:
    query = state["user_query"].lower()

    for pat in _REFUSE_PATTERNS:
        if pat in query:
            return {"intent": "refuse"}

    for kw in _DATA_KEYWORDS:
        if kw in query:
            return {"intent": "data"}

    for kw in _RAG_KEYWORDS:
        if kw in query:
            return {"intent": "rag"}

    # LLM fallback for ambiguous queries
    try:
        llm = ChatOllama(base_url=settings.OLLAMA_BASE_URL, model=settings.OLLAMA_MODEL)
        response = llm.invoke([
            SystemMessage(content=_SYSTEM_PROMPT),
            HumanMessage(content=state["user_query"]),
        ])
        raw = response.content.strip().lower()
        for intent in ("refuse", "data", "rag", "general"):
            if intent in raw:
                logger.info("Supervisor LLM → %s", intent)
                return {"intent": intent}
    except Exception as exc:
        logger.warning("Supervisor LLM failed (%s), defaulting to general", exc)

    return {"intent": "general"}
