"""General agent — direct LLM response without RAG."""
from __future__ import annotations
import logging
from typing import Any
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from src.config import settings
from src.graph.state import OrbitaState

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """Você é o Órbita, um assistente financeiro pessoal inteligente e amigável.
Responda em português do Brasil de forma concisa, clara e útil.
Você tem acesso a dados financeiros do usuário via Open Finance (Pluggy) e pode ajudar com
educação financeira baseada em livros clássicos como Pai Rico Pai Pobre, O Homem Mais Rico
da Babilônia e O Investidor Inteligente.
Para perguntas gerais, responda diretamente sem inventar dados financeiros específicos."""


def general_node(state: OrbitaState) -> dict[str, Any]:
    """Respond directly with the LLM, no RAG needed."""
    query = state["user_query"]
    logger.info("General node: %s", query[:60])
    try:
        llm = ChatOllama(base_url=settings.OLLAMA_BASE_URL, model=settings.OLLAMA_MODEL)
        response = llm.invoke([
            SystemMessage(content=_SYSTEM_PROMPT),
            HumanMessage(content=query),
        ])
        return {"final_response": response.content.strip(), "self_check_passed": True}
    except Exception as exc:
        logger.warning("General LLM failed: %s", exc)
        return {
            "final_response": "Desculpe, não consegui processar sua mensagem. Tente novamente.",
            "self_check_passed": True,
        }
