"""
agents/diet_agent.py
Diet Recommendation Agent — generates personalised weekly meal plans using
IBM Granite via watsonx.ai, taking into account the user's health profile,
Indian food preferences, allergies, and fitness goals.
"""

import logging
from typing import Any

from agents.llm_client import generate

logger = logging.getLogger(__name__)

# ── editable instructions ────────────────────────────────────────────────────

DIET_AGENT_INSTRUCTIONS: str = """
You are NutriSage Diet Planner, a specialist in creating personalised Indian
meal plans powered by IBM Granite.

ROLE
────
Generate a practical, healthy, and culturally appropriate 7-day meal plan
based on the user's profile. Favour Indian foods (dal, roti, sabzi, rice,
idli, dosa, poha, upma, khichdi, curd, paneer, etc.) unless the user
specifies otherwise.

PLAN FORMAT
───────────
For each day provide:
  Breakfast | Mid-morning snack | Lunch | Evening snack | Dinner
List the food items with approximate quantities (e.g., "2 rotis", "1 cup dal").
Add a one-line nutrition tip at the end of each day.

OUTPUT FORMAT
─────────────
Return the plan as plain text with clear day headings (Day 1, Day 2, …).
End with a short summary of estimated daily calories and macros for the plan.

PERSONALISATION RULES
─────────────────────
• Respect allergies and diseases strictly (e.g., no nuts if nut allergy, low
  sugar for diabetes, low sodium for hypertension).
• Adjust calorie target based on goal: weight loss (~300–500 kcal deficit),
  muscle gain (~300–500 kcal surplus), maintenance (TDEE).
• For vegetarians/vegans ensure adequate protein from plant sources.
• Include locally available, affordable Indian ingredients.

SAFETY
──────
Always add: "Consult a qualified dietitian before starting any new diet plan,
especially if you have a medical condition."
""".strip()


DIET_PROMPT_TEMPLATE: str = """
{instructions}

USER PROFILE
────────────
Name       : {name}
Age        : {age}
Gender     : {gender}
Weight     : {weight_kg} kg
Height     : {height_cm} cm
BMI        : {bmi:.1f} ({bmi_category})
Goal       : {goal}
Activity   : {activity}
Diet type  : {diet_type}
Allergies  : {allergies}
Diseases   : {diseases}
Preferences: {preferences}

Please generate a 7-day personalised Indian meal plan for this person.

MEAL PLAN
─────────
""".strip()


class DietAgent:
    """Generates personalised 7-day meal plans using IBM Granite."""

    def generate_plan(self, profile: dict[str, Any]) -> dict[str, Any]:
        from utils.bmi_calculator import calculate_bmi
        weight = float(profile.get("weight_kg", 60))
        height = float(profile.get("height_cm", 165))
        bmi_result = calculate_bmi(weight, height)

        prompt = DIET_PROMPT_TEMPLATE.format(
            instructions = DIET_AGENT_INSTRUCTIONS,
            name         = profile.get("name", "User"),
            age          = profile.get("age", "N/A"),
            gender       = profile.get("gender", "N/A"),
            weight_kg    = weight,
            height_cm    = height,
            bmi          = bmi_result["bmi"],
            bmi_category = bmi_result["category"],
            goal         = profile.get("goal", "maintain weight"),
            activity     = profile.get("activity", "moderately active"),
            diet_type    = profile.get("diet_type", "vegetarian"),
            allergies    = profile.get("allergies", "none"),
            diseases     = profile.get("diseases", "none"),
            preferences  = profile.get("preferences", "Indian cuisine"),
        )

        logger.info("Generating diet plan for goal=%s", profile.get("goal"))
        plan_text = generate(prompt)
        return {
            "plan": plan_text,
            "bmi": bmi_result["bmi"],
            "bmi_category": bmi_result["category"],
        }
