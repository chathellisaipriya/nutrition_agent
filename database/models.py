"""
database/models.py — SQLAlchemy ORM models for the Nutrition Agent.
"""

from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class FamilyMember(db.Model):
    __tablename__ = "family_members"

    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(100), nullable=False)
    age        = db.Column(db.Integer)
    gender     = db.Column(db.String(20))
    weight_kg  = db.Column(db.Float)
    height_cm  = db.Column(db.Float)
    goal       = db.Column(db.String(100))
    allergies  = db.Column(db.Text, default="")
    diseases   = db.Column(db.Text, default="")
    diet_type  = db.Column(db.String(50), default="vegetarian")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    food_logs  = db.relationship("FoodLog",  backref="member", lazy=True, cascade="all, delete-orphan")
    meal_plans = db.relationship("MealPlan", backref="member", lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id":        self.id,
            "name":      self.name,
            "age":       self.age,
            "gender":    self.gender,
            "weight_kg": self.weight_kg,
            "height_cm": self.height_cm,
            "goal":      self.goal,
            "allergies": self.allergies,
            "diseases":  self.diseases,
            "diet_type": self.diet_type,
        }


class FoodLog(db.Model):
    __tablename__ = "food_logs"

    id         = db.Column(db.Integer, primary_key=True)
    member_id  = db.Column(db.Integer, db.ForeignKey("family_members.id"), nullable=True)
    food_name  = db.Column(db.String(200), nullable=False)
    quantity   = db.Column(db.String(100), default="1 serving")
    calories   = db.Column(db.Float, default=0)
    protein_g  = db.Column(db.Float, default=0)
    carbs_g    = db.Column(db.Float, default=0)
    fat_g      = db.Column(db.Float, default=0)
    notes      = db.Column(db.Text, default="")
    logged_at  = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id":        self.id,
            "member_id": self.member_id,
            "food_name": self.food_name,
            "quantity":  self.quantity,
            "calories":  self.calories,
            "protein_g": self.protein_g,
            "carbs_g":   self.carbs_g,
            "fat_g":     self.fat_g,
            "notes":     self.notes,
            "logged_at": self.logged_at.strftime("%Y-%m-%d %H:%M") if self.logged_at else None,
        }


class MealPlan(db.Model):
    __tablename__ = "meal_plans"

    id         = db.Column(db.Integer, primary_key=True)
    member_id  = db.Column(db.Integer, db.ForeignKey("family_members.id"), nullable=True)
    goal       = db.Column(db.String(100))
    plan_text  = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id":         self.id,
            "member_id":  self.member_id,
            "goal":       self.goal,
            "plan_text":  self.plan_text,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M") if self.created_at else None,
        }
