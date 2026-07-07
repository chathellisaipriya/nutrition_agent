# agents/nutrition_agent.py
# Core NutritionAgent class:
#   1. Retrieves relevant chunks from the FAISS vector store (RAG).
#   2. Assembles a structured prompt using AGENT_INSTRUCTIONS + context.
#   3. Calls the IBM Granite model via llm_client.generate().
#   4. Returns the response along with source metadata.

import logging
from dataclasses import dataclass, field
from typing import List

from langchain.schema import Document

from agents.instructions import (
    AGENT_INSTRUCTIONS,
    NO_CONTEXT_PROMPT_TEMPLATE,
    RAG_PROMPT_TEMPLATE,
)
from agents.llm_client import generate
from rag.retriever import NutritionRetriever, build_retriever

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Response data class
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class AgentResponse:
    """Structured response returned by :class:`NutritionAgent`."""

    answer: str
    """The Granite model's generated answer."""

    sources: List[str] = field(default_factory=list)
    """File names of the retrieved context chunks (de-duplicated)."""

    context_used: bool = False
    """True when at least one RAG chunk was included in the prompt."""

    retrieved_chunks: List[Document] = field(default_factory=list)
    """The raw LangChain Document chunks that were retrieved (for debugging)."""

    def to_dict(self) -> dict:
        return {
            "answer": self.answer,
            "sources": self.sources,
            "context_used": self.context_used,
        }


# ─────────────────────────────────────────────────────────────────────────────
# Agent
# ─────────────────────────────────────────────────────────────────────────────

class NutritionAgent:
    """
    AI Nutrition Knowledge Agent powered by IBM Granite via watsonx.ai.

    Usage
    -----
    ::

        agent = NutritionAgent()
        response = agent.ask("What are good sources of iron in Indian food?")
        print(response.answer)
        print("Sources:", response.sources)
    """

    def __init__(
        self,
        retriever: NutritionRetriever | None = None,
        instructions: str | None = None,
    ):
        """
        Parameters
        ----------
        retriever:    Pre-built retriever. When *None*, :func:`build_retriever`
                      is called automatically (requires a built FAISS index).
        instructions: Override the default ``AGENT_INSTRUCTIONS`` string.
                      Useful for A/B testing different personas.
        """
        self._instructions = instructions or AGENT_INSTRUCTIONS
        self._retriever = retriever
        logger.info("NutritionAgent initialised.")

    # ── lazy-load retriever so the agent can be instantiated even before
    #    the FAISS index is built (e.g., at import time in app.py).
    @property
    def retriever(self) -> NutritionRetriever:
        if self._retriever is None:
            logger.info("No retriever provided — building from persisted index.")
            self._retriever = build_retriever()
        return self._retriever

    # ── internal helpers ──────────────────────────────────────────────────────

    def _retrieve_context(self, question: str) -> List[Document]:
        """Return top-k relevant chunks for *question*."""
        try:
            return self.retriever.retrieve(question)
        except Exception as exc:
            logger.warning("RAG retrieval failed (%s) — proceeding without context.", exc)
            return []

    @staticmethod
    def _format_context(chunks: List[Document]) -> str:
        """Concatenate chunk texts into a readable context block."""
        sections = []
        for i, doc in enumerate(chunks, start=1):
            source = doc.metadata.get("source", "unknown")
            sections.append(f"[{i}] (source: {source})\n{doc.page_content.strip()}")
        return "\n\n".join(sections)

    @staticmethod
    def _extract_sources(chunks: List[Document]) -> List[str]:
        """Return a de-duplicated, ordered list of source filenames."""
        seen: set[str] = set()
        sources: List[str] = []
        for doc in chunks:
            src = doc.metadata.get("source", "unknown")
            if src not in seen:
                seen.add(src)
                sources.append(src)
        return sources

    def _build_prompt(self, question: str, chunks: List[Document]) -> str:
        """Assemble the full prompt from instructions, context, and question."""
        if chunks:
            context_text = self._format_context(chunks)
            return RAG_PROMPT_TEMPLATE.format(
                system_instructions=self._instructions,
                context=context_text,
                question=question,
            )
        return NO_CONTEXT_PROMPT_TEMPLATE.format(
            system_instructions=self._instructions,
            question=question,
        )

    # ── public API ────────────────────────────────────────────────────────────

    def ask(self, question: str) -> AgentResponse:
        """
        Answer a nutrition question using RAG + IBM Granite.

        Parameters
        ----------
        question: The user's natural-language nutrition question.

        Returns
        -------
        :class:`AgentResponse`
            Contains the generated answer, sources used, and debug info.
        """
        if not question or not question.strip():
            return AgentResponse(answer="Please ask a nutrition-related question.")

        logger.info("Processing question: %r", question[:100])

        # 1. Retrieve relevant context
        chunks = self._retrieve_context(question)

        # 2. Build prompt
        prompt = self._build_prompt(question, chunks)
        logger.debug("Assembled prompt (%d chars).", len(prompt))

        # 3. Generate answer
        answer = generate(prompt)

        # 4. Build response object
        response = AgentResponse(
            answer=answer,
            sources=self._extract_sources(chunks),
            context_used=bool(chunks),
            retrieved_chunks=chunks,
        )
        logger.info(
            "Answer generated (%d chars, context_used=%s, sources=%s).",
            len(answer),
            response.context_used,
            response.sources,
        )
        return response

    def update_instructions(self, new_instructions: str) -> None:
        """
        Hot-swap the agent instructions at runtime without rebuilding the agent.

        Parameters
        ----------
        new_instructions: Replacement system-prompt string.
        """
        self._instructions = new_instructions
        logger.info("Agent instructions updated (%d chars).", len(new_instructions))
