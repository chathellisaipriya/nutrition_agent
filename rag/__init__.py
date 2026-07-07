# rag/__init__.py
# Public API for the RAG package.
#
# Typical usage from other modules:
#
#   from rag import ingest, build_retriever
#
#   ingest()                                  # index all docs in rag/data/
#   retriever = build_retriever()
#   docs = retriever.retrieve("Best protein sources?")

from rag.document_loader import load_documents, split_documents
from rag.embedder import get_embeddings
from rag.vector_store import build_vector_store, get_or_build_vector_store, load_vector_store
from rag.retriever import NutritionRetriever, build_retriever
from rag.pipeline import ingest

__all__ = [
    # document loading
    "load_documents",
    "split_documents",
    # embedding
    "get_embeddings",
    # vector store
    "build_vector_store",
    "load_vector_store",
    "get_or_build_vector_store",
    # retrieval
    "NutritionRetriever",
    "build_retriever",
    # high-level pipeline
    "ingest",
]
