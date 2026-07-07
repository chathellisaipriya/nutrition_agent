# rag/pipeline.py
# End-to-end ingestion pipeline: load → split → embed → persist.
# Run this once (or whenever documents are updated) to build the FAISS index.
#
# CLI usage:
#   python -m rag.pipeline
#
# Programmatic usage:
#   from rag import ingest
#   ingest()

import logging
import sys

from config import Config
from rag.document_loader import load_documents, split_documents
from rag.vector_store import build_vector_store

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def ingest(
    data_dir: str | None = None,
    index_dir: str | None = None,
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> int:
    """
    Full ingestion pipeline: load documents → split → embed → save FAISS index.

    Parameters
    ----------
    data_dir:      Source folder of nutrition documents
                   (defaults to ``Config.RAG_DATA_DIR``).
    index_dir:     Destination for the FAISS index
                   (defaults to ``Config.FAISS_INDEX_DIR``).
    chunk_size:    Override ``Config.RAG_CHUNK_SIZE``.
    chunk_overlap: Override ``Config.RAG_CHUNK_OVERLAP``.

    Returns
    -------
    int
        Number of chunks indexed.
    """
    data_dir = data_dir or Config.RAG_DATA_DIR
    index_dir = index_dir or Config.FAISS_INDEX_DIR

    logger.info("=== RAG ingestion pipeline started ===")
    logger.info("Data dir  : %s", data_dir)
    logger.info("Index dir : %s", index_dir)

    # 1. Load
    docs = load_documents(data_dir)
    if not docs:
        logger.error(
            "No documents found in '%s'. "
            "Add .pdf or .txt files and re-run.",
            data_dir,
        )
        return 0

    # 2. Split
    chunks = split_documents(docs, chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    # 3. Embed + persist
    build_vector_store(chunks, index_dir=index_dir)

    logger.info("=== Ingestion complete: %d chunks indexed ===", len(chunks))
    return len(chunks)


if __name__ == "__main__":
    count = ingest()
    sys.exit(0 if count > 0 else 1)
