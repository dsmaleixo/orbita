"""Text chunking configuration for document ingestion."""
from __future__ import annotations

from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


def get_text_splitter() -> RecursiveCharacterTextSplitter:
    """Return a configured text splitter for financial documents."""
    return RecursiveCharacterTextSplitter(
        chunk_size=512,
        chunk_overlap=50,
        length_function=len,
        separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""],
        keep_separator=False,
    )


def split_documents(documents: List[Document]) -> List[Document]:
    """Split documents into chunks, preserving metadata."""
    splitter = get_text_splitter()
    chunks = splitter.split_documents(documents)
    # Ensure each chunk retains its parent document's metadata
    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_index"] = i
    return chunks
