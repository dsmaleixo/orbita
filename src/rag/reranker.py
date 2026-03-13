"""Optional cross-encoder reranker using bge-reranker-v2-m3."""
from __future__ import annotations

import logging
from functools import lru_cache
from typing import List

from langchain_core.documents import Document

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _load_cross_encoder(model_name: str):
    """Load and cache a CrossEncoder model."""
    try:
        from sentence_transformers import CrossEncoder
        logger.info("Loading reranker model: %s", model_name)
        return CrossEncoder(model_name)
    except ImportError:
        logger.error("sentence-transformers not installed. Reranker unavailable.")
        return None


class CrossEncoderReranker:
    """Reranks retrieved documents using a cross-encoder model."""

    def __init__(self, model_name: str = "BAAI/bge-reranker-v2-m3", top_n: int = 3) -> None:
        self.model_name = model_name
        self.top_n = top_n

    def rerank(self, query: str, documents: List[Document]) -> List[Document]:
        """Rerank documents by cross-encoder relevance score."""
        if not documents:
            return documents

        model = _load_cross_encoder(self.model_name)
        if model is None:
            logger.warning("Reranker not available, returning documents unchanged.")
            return documents

        pairs = [(query, doc.page_content) for doc in documents]
        scores = model.predict(pairs)

        scored = sorted(zip(scores, documents), key=lambda x: x[0], reverse=True)
        reranked = [doc for _, doc in scored[: self.top_n]]
        logger.debug(
            "Reranked %d docs → top %d (scores: %s)",
            len(documents),
            self.top_n,
            [round(s, 3) for s, _ in scored[: self.top_n]],
        )
        return reranked
