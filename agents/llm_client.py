# agents/llm_client.py
# Thin wrapper around ibm-watsonx-ai that returns an initialised ModelInference
# client, applying generation parameters from Config.
# All other agent modules import from here — swap the underlying SDK in one place.

import logging
from functools import lru_cache

from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams

from config import Config

logger = logging.getLogger(__name__)


def _build_gen_params() -> dict:
    """Assemble the generation-parameter dict from Config."""
    return {
        GenParams.MAX_NEW_TOKENS: Config.LLM_MAX_NEW_TOKENS,
        GenParams.MIN_NEW_TOKENS: Config.LLM_MIN_NEW_TOKENS,
        GenParams.TEMPERATURE: Config.LLM_TEMPERATURE,
        GenParams.TOP_P: Config.LLM_TOP_P,
        GenParams.TOP_K: Config.LLM_TOP_K,
        GenParams.REPETITION_PENALTY: Config.LLM_REPETITION_PENALTY,
    }


@lru_cache(maxsize=1)
def get_llm_client() -> ModelInference:
    """
    Return a cached :class:`ModelInference` instance connected to the
    Granite model specified in ``Config.MODEL_ID``.

    The client is constructed once per process lifetime (``lru_cache``).
    Call :func:`reset_llm_client` in tests to force re-initialisation.

    Raises
    ------
    ValueError
        If ``IBM_API_KEY`` or ``PROJECT_ID`` are not configured.
    """
    if not Config.IBM_API_KEY:
        raise ValueError(
            "IBM_API_KEY is not set. Add it to your .env file."
        )
    if not Config.PROJECT_ID:
        raise ValueError(
            "PROJECT_ID is not set. Add it to your .env file."
        )
    print("IBM_URL =", repr(Config.IBM_URL))
    print("IBM_API_KEY exists =", bool(Config.IBM_API_KEY))
    credentials = Credentials(
        url=Config.IBM_URL,
        api_key=Config.IBM_API_KEY,
    )

    client = ModelInference(
        model_id=Config.MODEL_ID,
        credentials=credentials,
        project_id=Config.PROJECT_ID,
        params=_build_gen_params(),
    )

    logger.info(
        "watsonx.ai client initialised — model: %s  url: %s",
        Config.MODEL_ID,
        Config.IBM_URL,
    )
    return client


def generate(prompt: str, client: ModelInference | None = None) -> str:
    """
    Send *prompt* to the Granite model and return the generated text.

    Parameters
    ----------
    prompt: The fully assembled prompt string.
    client: Optional pre-built client (useful for testing). When *None* the
            module-level cached client is used.

    Returns
    -------
    str
        The model's response text, stripped of leading/trailing whitespace.
    """
    llm = client or get_llm_client()
    logger.debug("Sending prompt (%d chars) to Granite …", len(prompt))
    response = llm.generate_text(prompt=prompt)
    text: str = response.strip() if isinstance(response, str) else str(response).strip()
    logger.debug("Received response (%d chars).", len(text))
    return text


def reset_llm_client() -> None:
    """Clear the cached LLM client (useful in tests or after config changes)."""
    get_llm_client.cache_clear()
    logger.info("LLM client cache cleared.")
