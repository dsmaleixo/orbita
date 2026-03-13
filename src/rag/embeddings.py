"""bge-m3 embedding wrapper — singleton to avoid reloading."""
from __future__ import annotations

import logging
from functools import lru_cache
from typing import List

from langchain_huggingface import HuggingFaceEmbeddings

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_embeddings(model_name: str = "BAAI/bge-m3") -> HuggingFaceEmbeddings:
    """Return a cached HuggingFaceEmbeddings instance.

    Uses lru_cache so the model is loaded only once per process lifetime,
    avoiding expensive repeated loads during graph execution.
    """
    logger.info("Loading embedding model: %s", model_name)
    embeddings = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )
    logger.info("Embedding model loaded successfully.")
    return embeddings


def embed_query(text: str, model_name: str = "BAAI/bge-m3") -> List[float]:
    """Embed a single query string."""
    return get_embeddings(model_name).embed_query(text)


def embed_documents(texts: List[str], model_name: str = "BAAI/bge-m3") -> List[List[float]]:
    """Embed a list of document strings."""
    return get_embeddings(model_name).embed_documents(texts)
