"""FAISS vector store wrapper with load/save/search capabilities."""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import List, Optional

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from src.rag.embeddings import get_embeddings

logger = logging.getLogger(__name__)


class VectorStore:
    """Manages a local FAISS index for the Órbita document corpus."""

    def __init__(self, index_path: Optional[str] = None) -> None:
        from src.config import settings

        self.index_path = Path(index_path or settings.faiss_index_path)
        self.embed_model_name = settings.EMBED_MODEL
        self._store: Optional[FAISS] = None

    def _embeddings(self) -> object:
        return get_embeddings(self.embed_model_name)

    def load(self) -> None:
        """Load FAISS index from disk."""
        if not (self.index_path / "index.faiss").exists():
            raise FileNotFoundError(
                f"FAISS index not found at {self.index_path}. "
                "Run 'python -m ingest.pipeline' first."
            )
        logger.info("Loading FAISS index from %s", self.index_path)
        self._store = FAISS.load_local(
            str(self.index_path),
            self._embeddings(),
            allow_dangerous_deserialization=True,
        )
        logger.info("FAISS index loaded.")

    def save(self) -> None:
        """Persist FAISS index to disk."""
        if self._store is None:
            raise RuntimeError("No index to save. Build the index first.")
        self.index_path.mkdir(parents=True, exist_ok=True)
        self._store.save_local(str(self.index_path))
        logger.info("FAISS index saved to %s", self.index_path)

    def add_documents(self, documents: List[Document]) -> None:
        """Add documents to the index (used during ingest)."""
        if self._store is None:
            self._store = FAISS.from_documents(documents, self._embeddings())
        else:
            self._store.add_documents(documents)

    def search(self, query: str, k: int = 5) -> List[Document]:
        """Perform dense similarity search, returning top-k documents."""
        if self._store is None:
            try:
                self.load()
            except FileNotFoundError:
                logger.warning("FAISS index not available, returning empty results.")
                return []
        results = self._store.similarity_search(query, k=k)
        return results

    def search_with_scores(self, query: str, k: int = 5) -> List[tuple[Document, float]]:
        """Search and return (document, score) tuples."""
        if self._store is None:
            try:
                self.load()
            except FileNotFoundError:
                return []
        return self._store.similarity_search_with_score(query, k=k)

    @property
    def is_loaded(self) -> bool:
        return self._store is not None


# Module-level singleton for use across agents
_vectorstore_instance: Optional[VectorStore] = None


def get_vectorstore() -> VectorStore:
    """Return a module-level VectorStore singleton."""
    global _vectorstore_instance
    if _vectorstore_instance is None:
        _vectorstore_instance = VectorStore()
    return _vectorstore_instance
