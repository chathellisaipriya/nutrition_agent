"""
agents/food_log_agent.py
Food Log & Feedback Agent — estimates nutritional content of a logged food
item and provides daily dietary feedback using IBM Granite.
"""

import json
import logging
import re
from typing import Any

from agents.llm_client import generate

logger = logging.getLogger(__name__)

# ── editable instructions ────────────────────────────────────────────────────

FOOD_LOG_AGENT_INSTRUCTIONS: str = """
You are NutriSage Food Analyst, an expert at estimating nutritional content
of Indian and international foods, powered by IBM Granite.

When asked to analyse a food item:
• Return ONLY valid JSON (no markdown fences, no extra text).
• Use this exact schema:
  {
    "calories":   <number, kcal>,
    "protein_g":  <number, grams>,
    "carbs_g":    <number, grams>,
    "fat_g":      <number, grams>,
    "fiber_g":    <number, grams>,
    "notes":      "<one helpful nutrition tip about this food>"
  }
• Base estimates on standard nutritional databases (USDA, IFCT).
• Account for the specified quantity (e.g., "2 rotis", "1 cup dal").
• For Indian foods use the Indian Food Composition Tables (IFCT) as reference.
""".strip()

FOOD_ANALYSE_TEMPLATE: str = """
{instructions}

Analyse this food entry and return JSON only:
Food  : {food_name}
Qty   : {quantity}

JSON:
""".strip()

DAILY_FEEDBACK_INSTRUCTIONS: str = """
You are NutriSage Daily Coach. Review the user's food log for today and
provide friendly, encouraging, and practical feedback in 3–5 bullet points:
• Comment on overall calorie intake vs a typical 2000 kcal target.
• Highlight any nutritional gaps (protein, fibre, vitamins).
• Give one specific improvement suggestion using an Indian food.
• End on an encouraging note.
Keep the total response under 150 words.
""".strip()

DAILY_FEEDBACK_TEMPLATE: str = """
{instructions}

TODAY'S FOOD LOG
────────────────
{log_summary}

Total: {total_cal:.0f} kcal | Protein {total_protein:.1f}g | Carbs {total_carbs:.1f}g | Fat {total_fat:.1f}g

FEEDBACK
────────
""".strip()


class FoodLogAgent:
    """Estimates nutrition for logged foods and generates daily feedback."""

    # ── food analysis ─────────────────────────────────────────────────────────

    def analyse(self, food_name: str, quantity: str = "1 serving") -> dict[str, Any]:
        prompt = FOOD_ANALYSE_TEMPLATE.format(
            instructions = FOOD_LOG_AGENT_INSTRUCTIONS,
            food_name    = food_name,
            quantity     = quantity,
        )
        logger.info("Analysing food: %s (%s)", food_name, quantity)
        raw = generate(prompt)
        return self._parse_json(raw, food_name)

    # ── daily feedback ────────────────────────────────────────────────────────

    def daily_feedback(self, logs: list[dict]) -> dict[str, Any]:
        if not logs:
            return {
                "feedback": "No food logged today. Start by adding your first meal!",
                "total_calories": 0,
            }

        total_cal     = sum(l.get("calories",  0) for l in logs)
        total_protein = sum(l.get("protein_g", 0) for l in logs)
        total_carbs   = sum(l.get("carbs_g",   0) for l in logs)
        total_fat     = sum(l.get("fat_g",     0) for l in logs)

        log_lines = "\n".join(
            f"• {l['food_name']} ({l.get('quantity','')}) — {l.get('calories',0):.0f} kcal"
            for l in logs
        )

        prompt = DAILY_FEEDBACK_TEMPLATE.format(
            instructions  = DAILY_FEEDBACK_INSTRUCTIONS,
            log_summary   = log_lines,
            total_cal     = total_cal,
            total_protein = total_protein,
            total_carbs   = total_carbs,
            total_fat     = total_fat,
        )

        logger.info("Generating daily feedback for %d log entries.", len(logs))
        feedback_text = generate(prompt)
        return {
            "feedback":       feedback_text,
            "total_calories": round(total_cal, 1),
            "total_protein":  round(total_protein, 1),
            "total_carbs":    round(total_carbs, 1),
            "total_fat":      round(total_fat, 1),
        }

    # ── helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _parse_json(raw: str, food_name: str) -> dict[str, Any]:
        """Extract and parse JSON from LLM output, falling back to defaults."""
        try:
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if match:
                return json.loads(match.group())
        except (json.JSONDecodeError, AttributeError):
            pass
        logger.warning("Could not parse JSON for '%s'; using defaults.", food_name)
        return {
            "calories":  150, "protein_g": 5,
            "carbs_g":   20,  "fat_g":     5,
            "fiber_g":   2,   "notes": "Nutritional estimate unavailable.",
        }
