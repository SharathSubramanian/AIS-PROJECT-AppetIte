# src/backend/config.py
import os
import torch
from typing import List

# ---------------- Model settings ----------------
MAX_INPUT_LEN = int(os.getenv("MAX_INPUT_LEN", "512"))
MAX_OUTPUT_LEN = int(os.getenv("MAX_OUTPUT_LEN", "256"))

TEMPERATURE = float(os.getenv("TEMPERATURE", "0.8"))
TOP_P = float(os.getenv("TOP_P", "0.95"))
TOP_K = int(os.getenv("TOP_K", "50"))
NUM_BEAMS = int(os.getenv("NUM_BEAMS", "4"))

MODEL_DIR = os.getenv("APPETITE_MODEL_DIR", "/app/model/flan_t5_appetite_lora")
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# ---------------- Database ----------------
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:////app/data/appetite.db")

# ---------------- JWT ----------------
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "super-secret-change-me")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", str(60 * 24)))

# ---------------- CORS ----------------
CORS_ORIGINS: List[str] = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8501",
    "http://127.0.0.1:8501",
]