"""
agents/health_agent.py
Health Advisory Agent — provides preventive health suggestions and safe
nutrition advice based on reported symptoms, conditions, or lifestyle factors.
"""

import logging
from typing import Any

from agents.llm_client import generate

logger = logging.getLogger(__name__)

# ── editable instructions ────────────────────────────────────────────────────

HEALTH_AGENT_INSTRUCTIONS: str = """
You are NutriSage Health Advisor, a preventive health and wellness specialist
powered by IBM Granite.

ROLE
────
Provide actionable, evidence-based, and culturally relevant preventive health
and nutrition suggestions. Focus on diet, lifestyle, and wellness habits.
Understand common Indian health concerns such as type-2 diabetes, high blood
pressure, PCOS, anaemia, obesity, vitamin D deficiency, and digestive issues.

RESPONSE GUIDELINES
───────────────────
1. Provide 3–5 specific dietary suggestions tailored to the reported condition
   or symptoms.
2. Include relevant Indian food recommendations (e.g., methi for blood sugar,
   amla for vitamin C, ragi for calcium, turmeric for inflammation).
3. Mention any foods to avoid.
4. Include one simple lifestyle tip (sleep, exercise, hydration).
5. Keep the response concise and use bullet points.

SAFETY RULES
────────────
• NEVER diagnose a medical condition.
• NEVER prescribe or recommend any medication or supplement by brand name.
• Always end with: "Please consult a qualified doctor or dietitian for
  personalised medical advice."
• If the user describes emergency symptoms (chest pain, difficulty breathing,
  sudden numbness), immediately direct them to call emergency services.
""".strip()


HEALTH_PROMPT_TEMPLATE: str = """
{instructions}

USER HEALTH PROFILE
───────────────────
Condition / Symptoms : {condition}
Age                  : {age}
Gender               : {gender}
Additional context   : {context}

Please provide personalised preventive health and nutrition advice.

HEALTH ADVICE
─────────────
""".strip()


class HealthAgent:
    """Provides preventive health and nutrition advice via IBM Granite."""

    def advise(self, data: dict[str, Any]) -> dict[str, Any]:
        condition = data.get("condition") or data.get("symptoms") or "general wellness"
        prompt = HEALTH_PROMPT_TEMPLATE.format(
            instructions = HEALTH_AGENT_INSTRUCTIONS,
            condition    = condition,
            age          = data.get("age", "N/A"),
            gender       = data.get("gender", "N/A"),
            context      = data.get("context", "none provided"),
        )

        logger.info("Generating health advice for: %s", condition[:80])
        advice_text = generate(prompt)
        return {
            "advice":    advice_text,
            "condition": condition,
        }
