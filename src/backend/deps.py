# src/backend/deps.py
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from .database import SessionLocal
from .auth import get_current_user_from_token
from . import models

# OAuth2 token dependency
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_db_dep():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user_dep(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db_dep),
) -> models.User:
    return get_current_user_from_token(token, db)


# -------- Model lazy loader for generation --------
import os
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from .config import MODEL_DIR, DEVICE

_model = None
_tokenizer = None


def get_device():
    return DEVICE


def get_model_and_tokenizer():
    global _model, _tokenizer
    if _model is None or _tokenizer is None:
        try:
            _tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
            _model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_DIR)
        except Exception:
            _tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-base")
            _model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-base")

        _model.to(DEVICE)
        _model.eval()
    return _model, _tokenizer