# rag/retriever.py
# High-level retrieval interface: given a user query, return the top-k most
# relevant nutrition document chunks from the FAISS vector store.

import logging
from typing import List

from langchain.schema import Document

from config import Config
from rag.vector_store import get_or_build_vector_store, load_vector_store

logger = logging.getLogger(__name__)


class NutritionRetriever:
    """
    Wraps a FAISS vector store and exposes a simple :meth:`retrieve` method.

    Usage
    -----
    ::

        retriever = NutritionRetriever()
        results = retriever.retrieve("How much protein does chicken have?")
        for doc in results:
            print(doc.page_content)
    """

    def __init__(self, index_dir: str | None = None, top_k: int | None = None):
        """
        Parameters
        ----------
        index_dir: Path to the persisted FAISS index directory.
                   Defaults to ``Config.FAISS_INDEX_DIR``.
        top_k:     Number of chunks to return per query.
                   Defaults to ``Config.RAG_TOP_K``.
        """
        self._top_k = top_k or Config.RAG_TOP_K
        self._store = load_vector_store(index_dir)
        logger.info(
            "NutritionRetriever ready (top_k=%d).", self._top_k
        )

    def retrieve(self, query: str, top_k: int | None = None) -> List[Document]:
        """
        Return the *top_k* most semantically similar chunks for *query*.

        Parameters
        ----------
        query:  The user's natural-language question.
        top_k:  Override the instance-level default for this single call.

        Returns a list of :class:`~langchain.schema.Document` objects,
        each with ``page_content`` and ``metadata`` (including ``source``).
        """
        k = top_k or self._top_k
        if not query or not query.strip():
            logger.warning("Empty query received — returning no results.")
            return []

        logger.debug("Retrieving top-%d chunks for query: %r", k, query)
        results: List[Document] = self._store.similarity_search(query, k=k)
        logger.info("Retrieved %d chunk(s).", len(results))
        return results

    def retrieve_with_scores(
        self, query: str, top_k: int | None = None
    ) -> List[tuple[Document, float]]:
        """
        Same as :meth:`retrieve` but returns ``(Document, score)`` tuples.
        Lower L2 distance scores indicate higher relevance.
        """
        k = top_k or self._top_k
        if not query or not query.strip():
            return []

        logger.debug(
            "Retrieving top-%d chunks with scores for query: %r", k, query
        )
        return self._store.similarity_search_with_score(query, k=k)


def build_retriever(
    index_dir: str | None = None, top_k: int | None = None
) -> NutritionRetriever:
    """
    Factory function: returns a ready-to-use :class:`NutritionRetriever`.
    Preferred over instantiating the class directly in application code.
    """
    return NutritionRetriever(index_dir=index_dir, top_k=top_k)
