"""
utils/bmi_calculator.py — BMI calculation with health classification and
calorie-target estimation.
"""

from typing import Any


# WHO classification
_BMI_RANGES = [
    (0,    18.5, "Underweight",       "warning"),
    (18.5, 25.0, "Normal weight",     "success"),
    (25.0, 30.0, "Overweight",        "warning"),
    (30.0, 35.0, "Obese (Class I)",   "danger"),
    (35.0, 40.0, "Obese (Class II)",  "danger"),
    (40.0, 999,  "Obese (Class III)", "danger"),
]


def calculate_bmi(
    weight_kg: float,
    height_cm: float,
    age: int | None = None,
    gender: str | None = None,
) -> dict[str, Any]:
    """
    Calculate BMI, classify it, and estimate TDEE (moderate activity).

    Returns a dict with: bmi, category, color, ideal_weight_range,
    tdee_estimate, advice.
    """
    if height_cm <= 0 or weight_kg <= 0:
        raise ValueError("weight and height must be positive numbers.")

    height_m = height_cm / 100.0
    bmi      = round(weight_kg / (height_m ** 2), 1)

    category = "Unknown"
    color    = "secondary"
    for lo, hi, cat, col in _BMI_RANGES:
        if lo <= bmi < hi:
            category = cat
            color    = col
            break

    # ideal weight range (BMI 18.5–24.9)
    ideal_low  = round(18.5 * height_m ** 2, 1)
    ideal_high = round(24.9 * height_m ** 2, 1)

    # Mifflin-St Jeor BMR with moderate activity factor (1.55)
    if age and gender:
        g = (gender or "").lower()
        if g in ("male", "m"):
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
        else:
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
        tdee = round(bmr * 1.55)
    else:
        tdee = None

    advice_map = {
        "Underweight":       "Focus on calorie-dense, nutrient-rich foods. Add nuts, dairy, legumes, and whole grains to your diet.",
        "Normal weight":     "Great job! Maintain your balanced diet with plenty of vegetables, whole grains, and lean proteins.",
        "Overweight":        "Consider a moderate calorie deficit (~300 kcal/day) with more vegetables, dal, and regular physical activity.",
        "Obese (Class I)":   "Consult a dietitian for a personalised plan. Focus on whole foods, reduce refined carbs and sugary drinks.",
        "Obese (Class II)":  "Medical supervision recommended. Prioritise low-GI foods, control portions, and increase daily movement.",
        "Obese (Class III)": "Please seek medical advice immediately for a structured weight-management programme.",
    }

    return {
        "bmi":               bmi,
        "category":          category,
        "color":             color,
        "ideal_weight_low":  ideal_low,
        "ideal_weight_high": ideal_high,
        "tdee_estimate":     tdee,
        "advice":            advice_map.get(category, ""),
    }
