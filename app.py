"""
app.py — Flask entry point for the AI-Powered Nutrition Agent.
All routes are defined here; agents are lazily initialised on first use.
"""

import logging
import os
from datetime import date, datetime

from flask import Flask, jsonify, render_template, request, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

from config import Config

# ── logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ── app factory ───────────────────────────────────────────────────────────────
app = Flask(__name__)
app.config.from_object(Config)
#app.config["SQLALCHEMY_DATABASE_URI"] = Config.SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
CORS(app)

# ── database ──────────────────────────────────────────────────────────────────
from database.models import db, FamilyMember, FoodLog, MealPlan   # noqa: E402
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
db_folder = os.path.join(BASE_DIR, "database")

os.makedirs(db_folder, exist_ok=True)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(db_folder, "nutrition.db")

db.init_app(app)

# ── lazy agent singletons ─────────────────────────────────────────────────────
_nutrition_agent = None
_diet_agent      = None
_health_agent    = None
_food_log_agent  = None


def _get_nutrition_agent():
    global _nutrition_agent
    if _nutrition_agent is None:
        from agents.nutrition_agent import NutritionAgent
        _nutrition_agent = NutritionAgent()
    return _nutrition_agent


def _get_diet_agent():
    global _diet_agent
    if _diet_agent is None:
        from agents.diet_agent import DietAgent
        _diet_agent = DietAgent()
    return _diet_agent


def _get_health_agent():
    global _health_agent
    if _health_agent is None:
        from agents.health_agent import HealthAgent
        _health_agent = HealthAgent()
    return _health_agent


def _get_food_log_agent():
    global _food_log_agent
    if _food_log_agent is None:
        from agents.food_log_agent import FoodLogAgent
        _food_log_agent = FoodLogAgent()
    return _food_log_agent


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE ROUTES
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat")
def chat():
    return render_template("chat.html")


@app.route("/dashboard")
def dashboard():
    logs  = FoodLog.query.order_by(FoodLog.logged_at.desc()).limit(7).all()
    plans = MealPlan.query.order_by(MealPlan.created_at.desc()).limit(3).all()
    return render_template("dashboard.html", logs=logs, plans=plans)


@app.route("/meal-planner")
def meal_planner():
    members = FamilyMember.query.all()
    return render_template("meal_planner.html", members=members)


@app.route("/food-log")
def food_log():
    logs = FoodLog.query.order_by(FoodLog.logged_at.desc()).limit(50).all()
    return render_template("food_log.html", logs=logs)


@app.route("/bmi-calculator")
def bmi_calculator():
    return render_template("bmi_calculator.html")


@app.route("/family-profiles")
def family_profiles():
    members = FamilyMember.query.all()
    return render_template("family_profiles.html", members=members)


# ═══════════════════════════════════════════════════════════════════════════════
# API — CHAT / NUTRITION Q&A
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/api/chat", methods=["POST"])
def api_chat():
    data     = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()
    if not question:
        return jsonify({"error": "question is required"}), 400
    try:
        resp = _get_nutrition_agent().ask(question)
        return jsonify(resp.to_dict())
    except Exception as exc:
        logger.exception("Chat error")
        return jsonify({"error": str(exc)}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# API — DIET RECOMMENDATION
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/api/diet-plan", methods=["POST"])
def api_diet_plan():
    data = request.get_json(silent=True) or {}
    required = ["age", "gender", "weight_kg", "height_cm", "goal"]
    missing  = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400
    try:
        resp = _get_diet_agent().generate_plan(data)
        # persist plan
        member_id = data.get("member_id")
        plan = MealPlan(
            member_id   = member_id,
            goal        = data["goal"],
            plan_text   = resp["plan"],
            created_at  = datetime.utcnow(),
        )
        db.session.add(plan)
        db.session.commit()
        resp["plan_id"] = plan.id
        return jsonify(resp)
    except Exception as exc:
        logger.exception("Diet plan error")
        return jsonify({"error": str(exc)}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# API — HEALTH ADVISORY
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/api/health-advice", methods=["POST"])
def api_health_advice():
    data = request.get_json(silent=True) or {}
    if not data.get("symptoms") and not data.get("condition"):
        return jsonify({"error": "symptoms or condition is required"}), 400
    try:
        resp = _get_health_agent().advise(data)
        return jsonify(resp)
    except Exception as exc:
        logger.exception("Health advice error")
        return jsonify({"error": str(exc)}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# API — FOOD LOG
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/api/food-log", methods=["POST"])
def api_food_log_add():
    data      = request.get_json(silent=True) or {}
    food_name = (data.get("food_name") or "").strip()
    if not food_name:
        return jsonify({"error": "food_name is required"}), 400
    try:
        analysis = _get_food_log_agent().analyse(food_name, data.get("quantity", "1 serving"))
        entry = FoodLog(
            member_id   = data.get("member_id"),
            food_name   = food_name,
            quantity    = data.get("quantity", "1 serving"),
            calories    = analysis.get("calories", 0),
            protein_g   = analysis.get("protein_g", 0),
            carbs_g     = analysis.get("carbs_g", 0),
            fat_g       = analysis.get("fat_g", 0),
            notes       = analysis.get("notes", ""),
            logged_at   = datetime.utcnow(),
        )
        db.session.add(entry)
        db.session.commit()
        return jsonify({"log_id": entry.id, **analysis})
    except Exception as exc:
        logger.exception("Food log error")
        return jsonify({"error": str(exc)}), 500


@app.route("/api/food-log", methods=["GET"])
def api_food_log_get():
    logs = FoodLog.query.order_by(FoodLog.logged_at.desc()).limit(50).all()
    return jsonify([l.to_dict() for l in logs])


@app.route("/api/food-log/<int:log_id>", methods=["DELETE"])
def api_food_log_delete(log_id):
    entry = FoodLog.query.get_or_404(log_id)
    db.session.delete(entry)
    db.session.commit()
    return jsonify({"deleted": log_id})


@app.route("/api/daily-feedback", methods=["GET"])
def api_daily_feedback():
    today = date.today()
    logs  = FoodLog.query.filter(
        db.func.date(FoodLog.logged_at) == today
    ).all()
    try:
        feedback = _get_food_log_agent().daily_feedback([l.to_dict() for l in logs])
        return jsonify(feedback)
    except Exception as exc:
        logger.exception("Daily feedback error")
        return jsonify({"error": str(exc)}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# API — BMI CALCULATOR
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/api/bmi", methods=["POST"])
def api_bmi():
    from utils.bmi_calculator import calculate_bmi
    data = request.get_json(silent=True) or {}
    try:
        weight = float(data["weight_kg"])
        height = float(data["height_cm"])
    except (KeyError, ValueError, TypeError):
        return jsonify({"error": "weight_kg and height_cm are required numbers"}), 400
    result = calculate_bmi(weight, height, data.get("age"), data.get("gender"))
    return jsonify(result)


# ═══════════════════════════════════════════════════════════════════════════════
# API — FAMILY PROFILES
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/api/family", methods=["GET"])
def api_family_list():
    members = FamilyMember.query.all()
    return jsonify([m.to_dict() for m in members])


@app.route("/api/family", methods=["POST"])
def api_family_add():
    data = request.get_json(silent=True) or {}
    if not data.get("name"):
        return jsonify({"error": "name is required"}), 400
    member = FamilyMember(
        name        = data["name"],
        age         = data.get("age"),
        gender      = data.get("gender"),
        weight_kg   = data.get("weight_kg"),
        height_cm   = data.get("height_cm"),
        goal        = data.get("goal", ""),
        allergies   = data.get("allergies", ""),
        diseases    = data.get("diseases", ""),
        diet_type   = data.get("diet_type", "vegetarian"),
    )
    db.session.add(member)
    db.session.commit()
    return jsonify(member.to_dict()), 201


@app.route("/api/family/<int:member_id>", methods=["PUT"])
def api_family_update(member_id):
    member = FamilyMember.query.get_or_404(member_id)
    data   = request.get_json(silent=True) or {}
    for field_name in ["name","age","gender","weight_kg","height_cm","goal","allergies","diseases","diet_type"]:
        if field_name in data:
            setattr(member, field_name, data[field_name])
    db.session.commit()
    return jsonify(member.to_dict())


@app.route("/api/family/<int:member_id>", methods=["DELETE"])
def api_family_delete(member_id):
    member = FamilyMember.query.get_or_404(member_id)
    db.session.delete(member)
    db.session.commit()
    return jsonify({"deleted": member_id})


# ═══════════════════════════════════════════════════════════════════════════════
# STARTUP
# ═══════════════════════════════════════════════════════════════════════════════

with app.app_context():
    os.makedirs("database", exist_ok=True)
    db.create_all()
    logger.info("Database tables ready.")


if __name__ == "__main__":
    app.run(
        host  = "0.0.0.0",
        port  = int(os.getenv("PORT", 5000)),
        debug = Config.DEBUG,
    )
