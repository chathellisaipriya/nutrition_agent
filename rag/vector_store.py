# rag/vector_store.py
# Manages the FAISS vector store: build from chunks, persist to disk,
# and reload an existing index without re-embedding.

import logging
import os
from pathlib import Path
from typing import List

from langchain.schema import Document
from langchain_community.vectorstores import FAISS

from config import Config
from rag.embedder import get_embeddings

logger = logging.getLogger(__name__)


def _index_path(index_dir: str | None = None) -> Path:
    return Path(index_dir or Config.FAISS_INDEX_DIR)


def build_vector_store(
    chunks: List[Document],
    index_dir: str | None = None,
) -> FAISS:
    """
    Embed *chunks* and persist a new FAISS index to *index_dir*.

    Any existing index at that location is overwritten.

    Parameters
    ----------
    chunks:    Text chunks from :func:`rag.document_loader.split_documents`.
    index_dir: Directory where the FAISS index files are saved
               (defaults to ``Config.FAISS_INDEX_DIR``).

    Returns the in-memory :class:`FAISS` vector store.
    """
    if not chunks:
        raise ValueError("Cannot build a vector store from an empty chunk list.")

    index_path = _index_path(index_dir)
    index_path.mkdir(parents=True, exist_ok=True)

    logger.info("Building FAISS index from %d chunks …", len(chunks))
    embeddings = get_embeddings()
    store = FAISS.from_documents(chunks, embeddings)
    store.save_local(str(index_path))
    logger.info("FAISS index saved to '%s'.", index_path)
    return store


def load_vector_store(index_dir: str | None = None) -> FAISS:
    """
    Load an existing FAISS index from *index_dir*.

    Raises
    ------
    FileNotFoundError
        If no persisted index is found at *index_dir*.
    """
    index_path = _index_path(index_dir)
    index_file = index_path / "index.faiss"

    if not index_file.exists():
        raise FileNotFoundError(
            f"No FAISS index found at '{index_path}'. "
            "Run build_vector_store() first."
        )

    logger.info("Loading FAISS index from '%s' …", index_path)
    embeddings = get_embeddings()
    store = FAISS.load_local(
        str(index_path),
        embeddings,
        allow_dangerous_deserialization=True,  # safe: local files we wrote
    )
    logger.info("FAISS index loaded successfully.")
    return store


def get_or_build_vector_store(
    chunks: List[Document] | None = None,
    index_dir: str | None = None,
) -> FAISS:
    """
    Convenience helper: load an existing index if one is present, otherwise
    build and save a new one from *chunks*.

    Parameters
    ----------
    chunks:    Required only when no persisted index exists.
    index_dir: Override for the index directory.
    """
    try:
        return load_vector_store(index_dir)
    except FileNotFoundError:
        logger.info("No existing index found — building from provided chunks.")
        if not chunks:
            raise ValueError(
                "chunks must be provided when no persisted index exists."
            )
        return build_vector_store(chunks, index_dir)
