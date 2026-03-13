"""Writer agent — generates citation-formatted responses."""
from __future__ import annotations

import logging
from typing import Any, List

from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama

from src.config import settings
from src.graph.state import OrbitaState

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """Você é o assistente educacional financeiro Órbita, especializado em educação
financeira para jovens brasileiros. Responda em português do Brasil.

REGRAS OBRIGATÓRIAS:
1. Use APENAS informações dos documentos fornecidos no contexto.
2. Cite a fonte de CADA afirmação usando o formato: [Fonte: {título}, p.{página}]
3. Se o contexto não tiver informação suficiente, diga claramente que não tem.
4. NUNCA faça recomendações de investimento específicas.
5. Seja educacional, claro e acessível para jovens (18-35 anos).
6. Respostas devem ser concisas (máximo 300 palavras).

FORMATO DA RESPOSTA:
- Resposta direta à pergunta
- Citações inline no formato [Fonte: X, p.Y]
- Resumo final em 1-2 frases"""


def _format_context(docs: List[Document]) -> str:
    """Format retrieved documents as context string."""
    if not docs:
        return "Nenhum documento relevante encontrado."

    parts = []
    for i, doc in enumerate(docs, 1):
        meta = doc.metadata
        title = meta.get("title", "Documento desconhecido")
        page = meta.get("page_number", 1)
        parts.append(f"[Documento {i}] {title} (p.{page}):\n{doc.page_content}")
    return "\n\n".join(parts)


def _extract_citations(docs: List[Document]) -> List[dict]:
    """Extract citation metadata from retrieved documents."""
    citations = []
    for doc in docs:
        meta = doc.metadata
        citations.append({
            "source": meta.get("title", "Fonte desconhecida"),
            "page": meta.get("page_number", 1),
            "url": meta.get("source_url", ""),
            "passage": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
        })
    return citations


def writer_node(state: OrbitaState) -> dict[str, Any]:
    """Generate a citation-formatted response using retrieved documents."""
    query = state["user_query"]
    docs = state.get("retrieved_docs", [])
    disclaimers = state.get("disclaimers", [])

    logger.info("Writer: generating response for: %.80s...", query)

    context = _format_context(docs)
    citations = _extract_citations(docs)

    user_message = f"""CONTEXTO DOS DOCUMENTOS:
{context}

PERGUNTA DO USUÁRIO:
{query}

Responda usando apenas o contexto acima, com citações inline [Fonte: X, p.Y]."""

    try:
        llm = ChatOllama(base_url=settings.OLLAMA_BASE_URL, model=settings.OLLAMA_MODEL)
        messages = [
            SystemMessage(content=_SYSTEM_PROMPT),
            HumanMessage(content=user_message),
        ]
        response = llm.invoke(messages)
        draft = response.content.strip()
        logger.info("Writer: generated response (%d chars)", len(draft))

    except Exception as exc:
        logger.warning("Writer LLM call failed: %s", exc)
        if docs:
            # Fallback: assemble response from context directly
            draft = f"Com base nos documentos disponíveis:\n\n{context[:500]}...\n\n[Fonte: {docs[0].metadata.get('title', 'Documento')}, p.{docs[0].metadata.get('page_number', 1)}]"
        else:
            draft = "Não encontrei informações suficientes para responder a essa pergunta."

    # Append disclaimers
    if disclaimers:
        draft = draft + "\n\n---\n" + "\n".join(disclaimers)

    return {
        "draft_response": draft,
        "citations": citations,
    }
