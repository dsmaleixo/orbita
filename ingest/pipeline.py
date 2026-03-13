"""End-to-end document ingestion pipeline.

Usage:
    python -m ingest.pipeline

This script:
1. Loads source definitions from ingest/sources.yaml
2. Downloads/loads each source (PDF or HTML)
3. Falls back to synthetic corpus if real sources are unavailable
4. Splits documents into chunks
5. Embeds chunks with bge-m3
6. Saves FAISS index to disk
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import List

import yaml
from langchain_core.documents import Document

# Allow running as __main__ from project root
sys.path.insert(0, str(Path(__file__).parent.parent))

from ingest.loaders import load_html, load_pdf, load_synthetic_corpus
from ingest.splitter import split_documents
from src.config import settings
from src.rag.vectorstore import VectorStore

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def load_sources_yaml() -> List[dict]:
    """Load source definitions from sources.yaml."""
    sources_path = Path(__file__).parent / "sources.yaml"
    with open(sources_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config.get("sources", [])


def run_pipeline() -> None:
    """Execute the full ingestion pipeline."""
    logger.info("=== Órbita Document Ingestion Pipeline ===")

    sources = load_sources_yaml()
    all_docs: List[Document] = []

    # Attempt to load real sources
    for source in sources:
        logger.info("Loading source: %s (%s)", source["id"], source["type"])
        if source["type"] == "pdf":
            docs = load_pdf(source["url"], source["title"], source["id"])
        elif source["type"] == "html":
            docs = load_html(source["url"], source["title"], source["id"])
        else:
            logger.warning("Unknown source type: %s", source["type"])
            docs = []
        all_docs.extend(docs)

    if not all_docs:
        logger.warning("No real documents loaded. Using synthetic corpus as fallback.")
        all_docs = load_synthetic_corpus()
    else:
        # Always include synthetic corpus to ensure core topics are covered
        logger.info("Augmenting with synthetic corpus for comprehensive coverage.")
        all_docs.extend(load_synthetic_corpus())

    logger.info("Total documents loaded: %d", len(all_docs))

    # Split into chunks
    chunks = split_documents(all_docs)
    logger.info("Total chunks after splitting: %d", len(chunks))

    # Build and save FAISS index
    vectorstore = VectorStore()
    logger.info("Building FAISS index (this may take a few minutes)...")
    vectorstore.add_documents(chunks)
    vectorstore.save()

    index_file = settings.faiss_index_path / "index.faiss"
    size_mb = index_file.stat().st_size / (1024 * 1024) if index_file.exists() else 0
    logger.info("Pipeline complete. Index size: %.2f MB", size_mb)
    logger.info("Index saved to: %s", settings.faiss_index_path)


if __name__ == "__main__":
    run_pipeline()
