"""Retriever agent — dense FAISS search with optional reranking."""
from __future__ import annotations

import logging
from typing import Any, List

from langchain_core.documents import Document

from src.config import settings
from src.graph.state import OrbitaState
from src.rag.vectorstore import get_vectorstore

logger = logging.getLogger(__name__)


def retriever_node(state: OrbitaState) -> dict[str, Any]:
    """Retrieve relevant documents from FAISS for the user query."""
    query = state["user_query"]
    attempts = state.get("retrieval_attempts", 0)

    logger.info("Retriever: attempt %d for query: %.80s...", attempts + 1, query)

    vectorstore = get_vectorstore()
    docs: List[Document] = vectorstore.search(query, k=5)

    # Optional reranking
    if settings.ENABLE_RERANKER and docs:
        try:
            from src.rag.reranker import CrossEncoderReranker
            reranker = CrossEncoderReranker(model_name=settings.RERANKER_MODEL, top_n=3)
            docs = reranker.rerank(query, docs)
            logger.info("Reranker applied, top %d docs returned", len(docs))
        except Exception as exc:
            logger.warning("Reranker failed: %s", exc)

    logger.info("Retrieved %d documents", len(docs))
    return {
        "retrieved_docs": docs,
        "retrieval_attempts": attempts + 1,
    }
