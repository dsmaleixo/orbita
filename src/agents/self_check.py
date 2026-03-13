"""Self-check agent — Self-RAG claim grounding validation."""
from __future__ import annotations

import logging
from typing import Any, List

from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama

from src.config import settings
from src.graph.state import OrbitaState

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """Você é um verificador de precisão factual para o assistente Órbita.

Analise a RESPOSTA GERADA e verifique se CADA afirmação factual está suportada pelo CONTEXTO DOS DOCUMENTOS.

Responda em JSON com o seguinte formato:
{
  "all_supported": true/false,
  "unsupported_claims": ["afirmação 1 não suportada", "afirmação 2 não suportada"]
}

Regras:
- "all_supported" é true APENAS se TODAS as afirmações têm suporte no contexto
- Liste apenas afirmações específicas que NÃO têm evidência no contexto
- Se não houver contexto suficiente, "all_supported" deve ser false
- Ignore disclaimers e frases de aviso na avaliação"""

_REFUSAL_MESSAGE = (
    "Não tenho evidências suficientes nos documentos disponíveis para responder "
    "a essa pergunta com precisão. Para garantir informações confiáveis, "
    "recomendo consultar diretamente o Banco Central do Brasil (bcb.gov.br), "
    "a CVM (investidor.gov.br), ou um profissional financeiro certificado.\n\n"
    "⚠️ Órbita é uma ferramenta educacional. Não constitui aconselhamento financeiro."
)


def _check_grounding_llm(query: str, draft: str, docs: List[Document]) -> tuple[bool, List[str]]:
    """Use LLM to verify claim grounding against retrieved documents."""
    if not docs:
        return False, ["Nenhum documento recuperado para verificar as afirmações."]

    context = "\n\n".join(
        f"[Doc {i+1}] {doc.metadata.get('title', '')}: {doc.page_content[:300]}"
        for i, doc in enumerate(docs)
    )

    user_message = f"""CONTEXTO DOS DOCUMENTOS:
{context}

RESPOSTA GERADA:
{draft[:800]}

Verifique se as afirmações da resposta estão suportadas pelo contexto."""

    try:
        import json
        llm = ChatOllama(
            base_url=settings.OLLAMA_BASE_URL,
            model=settings.OLLAMA_MODEL,
            format="json",
        )
        messages = [
            SystemMessage(content=_SYSTEM_PROMPT),
            HumanMessage(content=user_message),
        ]
        response = llm.invoke(messages)
        result = json.loads(response.content)
        all_supported = result.get("all_supported", False)
        unsupported = result.get("unsupported_claims", [])
        return all_supported, unsupported

    except Exception as exc:
        logger.warning("Self-check LLM call failed: %s. Falling back to heuristic check.", exc)
        return _check_grounding_heuristic(draft, docs)


def _check_grounding_heuristic(draft: str, docs: List[Document]) -> tuple[bool, List[str]]:
    """Simple heuristic: check if key terms in draft appear in retrieved docs."""
    if not docs:
        return False, ["Sem documentos para verificação"]

    all_content = " ".join(doc.page_content.lower() for doc in docs)
    draft_lower = draft.lower()

    # Extract key financial terms
    financial_terms = [
        "tesouro", "cdi", "poupança", "fgts", "inss", "selic", "ipca",
        "fundo", "ação", "cdb", "lci", "lca", "previdência"
    ]

    terms_in_draft = [t for t in financial_terms if t in draft_lower]
    terms_supported = [t for t in terms_in_draft if t in all_content]

    if not terms_in_draft:
        # No specific financial terms, assume OK
        return True, []

    support_ratio = len(terms_supported) / len(terms_in_draft) if terms_in_draft else 0
    if support_ratio >= settings.SELF_CHECK_THRESHOLD:
        return True, []
    else:
        unsupported = [t for t in terms_in_draft if t not in all_content]
        return False, [f"Termo '{t}' não encontrado nos documentos recuperados" for t in unsupported[:3]]


def self_check_node(state: OrbitaState) -> dict[str, Any]:
    """Validate that the draft response is grounded in retrieved documents."""
    draft = state.get("draft_response", "")
    docs = state.get("retrieved_docs", [])
    attempts = state.get("retrieval_attempts", 0)

    logger.info("Self-check: validating response (attempt %d)", attempts)

    if not draft:
        logger.warning("Self-check: no draft response to validate")
        return {
            "self_check_passed": False,
            "unsupported_claims": ["Nenhuma resposta gerada"],
            "final_response": _REFUSAL_MESSAGE,
        }

    all_supported, unsupported = _check_grounding_llm(state["user_query"], draft, docs)

    if all_supported:
        logger.info("Self-check: PASSED — all claims supported")
        return {
            "self_check_passed": True,
            "unsupported_claims": [],
            "final_response": draft,
        }

    logger.info(
        "Self-check: FAILED — %d unsupported claims, attempts=%d",
        len(unsupported),
        attempts,
    )

    if attempts >= settings.MAX_RETRIEVAL_ATTEMPTS:
        logger.info("Self-check: max retries reached, issuing refusal")
        return {
            "self_check_passed": False,
            "unsupported_claims": unsupported,
            "final_response": _REFUSAL_MESSAGE,
        }

    # Signal for re-retrieval (builder.py will route back to retriever)
    return {
        "self_check_passed": False,
        "unsupported_claims": unsupported,
        "final_response": "",
    }
