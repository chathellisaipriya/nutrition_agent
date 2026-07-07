# rag/embedder.py
# Builds a LangChain-compatible embedding object backed by
# sentence-transformers (runs locally, no API quota consumed).
# Drop-in replacement: swap SentenceTransformerEmbeddings for
# WatsonxEmbeddings when an embedding endpoint is available on watsonx.ai.

import logging

from langchain_community.embeddings import SentenceTransformerEmbeddings

from config import Config

logger = logging.getLogger(__name__)


def get_embeddings(model_name: str | None = None) -> SentenceTransformerEmbeddings:
    """
    Return a LangChain embedding object.

    The default model (``sentence-transformers/all-MiniLM-L6-v2``) is small
    (~80 MB), fast, and well-suited for semantic similarity over short text
    chunks.  Override ``EMBEDDING_MODEL`` in *.env* to use any other
    sentence-transformers model.

    Parameters
    ----------
    model_name: HuggingFace model id (defaults to ``Config.EMBEDDING_MODEL``).
    """
    model_name = model_name or Config.EMBEDDING_MODEL
    logger.info("Loading embedding model: %s", model_name)
    embeddings = SentenceTransformerEmbeddings(model_name=model_name)
    logger.info("Embedding model ready.")
    return embeddings
