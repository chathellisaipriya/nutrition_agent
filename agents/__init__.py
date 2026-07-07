# agents/__init__.py
from agents.instructions import (
    AGENT_INSTRUCTIONS,
    RAG_PROMPT_TEMPLATE,
    NO_CONTEXT_PROMPT_TEMPLATE,
)
from agents.llm_client import generate, get_llm_client, reset_llm_client
from agents.nutrition_agent import AgentResponse, NutritionAgent
from agents.diet_agent import DietAgent
from agents.health_agent import HealthAgent
from agents.food_log_agent import FoodLogAgent

__all__ = [
    "AGENT_INSTRUCTIONS", "RAG_PROMPT_TEMPLATE", "NO_CONTEXT_PROMPT_TEMPLATE",
    "get_llm_client", "generate", "reset_llm_client",
    "NutritionAgent", "AgentResponse",
    "DietAgent",
    "HealthAgent",
    "FoodLogAgent",
]
