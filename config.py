# config.py
# Central configuration for the Nutrition Agent application

import os
from dotenv import load_dotenv

# Load variables from .env into the process environment
load_dotenv()


class Config:
    # ── Flask ─────────────────────────────────────────────────────────────────
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me")
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"

    # ── IBM watsonx.ai ────────────────────────────────────────────────────────
    IBM_API_KEY = os.getenv("IBM_API_KEY", "")
    PROJECT_ID = os.getenv("PROJECT_ID", "")
    IBM_URL = os.getenv("IBM_URL", "https://us-south.ml.cloud.ibm.com")

    # ── Granite model ─────────────────────────────────────────────────────────
    MODEL_ID = os.getenv("MODEL_ID", "ibm/granite-3-2-8b-instruct")

    # ── File uploads ──────────────────────────────────────────────────────────
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

    # ── Database ──────────────────────────────────────────────────────────────
    SQLALCHEMY_DATABASE_URI = os.getenv(
    "SQLALCHEMY_DATABASE_URI",
    "sqlite:///database/nutrition.db"
)
    # ── RAG / Vector store ────────────────────────────────────────────────────
    RAG_DATA_DIR = os.getenv("RAG_DATA_DIR", "rag/data")
    FAISS_INDEX_DIR = os.getenv("FAISS_INDEX_DIR", "rag/faiss_index")
    EMBEDDING_MODEL = os.getenv(
        "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
    )
    RAG_CHUNK_SIZE = int(os.getenv("RAG_CHUNK_SIZE", "512"))
    RAG_CHUNK_OVERLAP = int(os.getenv("RAG_CHUNK_OVERLAP", "64"))
    RAG_TOP_K = int(os.getenv("RAG_TOP_K", "4"))

    # ── LLM generation parameters ─────────────────────────────────────────────
    LLM_MAX_NEW_TOKENS = int(os.getenv("LLM_MAX_NEW_TOKENS", "1024"))
    LLM_MIN_NEW_TOKENS = int(os.getenv("LLM_MIN_NEW_TOKENS", "50"))
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    LLM_TOP_P = float(os.getenv("LLM_TOP_P", "0.9"))
    LLM_TOP_K = int(os.getenv("LLM_TOP_K", "50"))
    LLM_REPETITION_PENALTY = float(os.getenv("LLM_REPETITION_PENALTY", "1.1"))
