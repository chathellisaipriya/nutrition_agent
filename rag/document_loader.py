# rag/document_loader.py
# Loads PDF and plain-text nutrition documents from the configured data directory
# and splits them into overlapping chunks ready for embedding.

import logging
import os
from pathlib import Path
from typing import List

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader

from config import Config

logger = logging.getLogger(__name__)


def _load_single_file(file_path: Path) -> List[Document]:
    """Return a list of LangChain Documents from one PDF or .txt file."""
    suffix = file_path.suffix.lower()
    try:
        if suffix == ".pdf":
            loader = PyPDFLoader(str(file_path))
        elif suffix in (".txt", ".md"):
            loader = TextLoader(str(file_path), encoding="utf-8")
        else:
            logger.warning("Skipping unsupported file type: %s", file_path.name)
            return []
        docs = loader.load()
        # Attach the source filename to every document's metadata
        for doc in docs:
            doc.metadata.setdefault("source", file_path.name)
        logger.info("Loaded %d page(s) from '%s'", len(docs), file_path.name)
        return docs
    except Exception as exc:
        logger.error("Failed to load '%s': %s", file_path.name, exc)
        return []


def load_documents(data_dir: str | None = None) -> List[Document]:
    """
    Walk *data_dir* (defaults to ``Config.RAG_DATA_DIR``) and load every
    supported document file (.pdf, .txt, .md).

    Returns a flat list of raw LangChain ``Document`` objects.
    """
    data_dir = data_dir or Config.RAG_DATA_DIR
    data_path = Path(data_dir)

    if not data_path.exists():
        logger.warning("Data directory '%s' does not exist — creating it.", data_dir)
        data_path.mkdir(parents=True, exist_ok=True)
        return []

    all_docs: List[Document] = []
    for file_path in sorted(data_path.iterdir()):
        if file_path.is_file():
            all_docs.extend(_load_single_file(file_path))

    if not all_docs:
        logger.warning("No documents found in '%s'.", data_dir)
    else:
        logger.info("Total pages loaded: %d", len(all_docs))

    return all_docs


def split_documents(
    docs: List[Document],
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> List[Document]:
    """
    Split raw documents into overlapping text chunks suitable for embedding.

    Parameters
    ----------
    docs:          List of Documents returned by :func:`load_documents`.
    chunk_size:    Max characters per chunk (defaults to ``Config.RAG_CHUNK_SIZE``).
    chunk_overlap: Overlap between consecutive chunks (defaults to
                   ``Config.RAG_CHUNK_OVERLAP``).

    Returns a list of chunk ``Document`` objects.
    """
    chunk_size = chunk_size or Config.RAG_CHUNK_SIZE
    chunk_overlap = chunk_overlap or Config.RAG_CHUNK_OVERLAP

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(docs)
    logger.info(
        "Split %d document page(s) into %d chunk(s) "
        "(size=%d, overlap=%d).",
        len(docs),
        len(chunks),
        chunk_size,
        chunk_overlap,
    )
    return chunks
