"""
utils/helpers.py — shared utility functions for the Nutrition Agent.
"""

from datetime import datetime


def format_datetime(dt: datetime | None) -> str:
    if not dt:
        return ""
    return dt.strftime("%d %b %Y, %I:%M %p")


def calories_color(calories: float) -> str:
    """Return a Bootstrap colour class based on calorie count."""
    if calories < 300:
        return "success"
    if calories < 600:
        return "warning"
    return "danger"


def truncate(text: str, max_len: int = 120) -> str:
    """Truncate long text with an ellipsis."""
    if not text:
        return ""
    return text[:max_len] + "…" if len(text) > max_len else text
