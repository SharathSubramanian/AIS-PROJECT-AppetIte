# src/backend/models.py
from __future__ import annotations
from datetime import datetime, date
from sqlalchemy import (
    Column, Integer, String, DateTime, Date, ForeignKey, Text
)
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, index=True, nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    hashed_password = Column(String(256), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    pantry_items = relationship("PantryItem", back_populates="owner", cascade="all, delete-orphan")
    shopping_lists = relationship("ShoppingList", back_populates="owner", cascade="all, delete-orphan")
    feedback_entries = relationship("Feedback", back_populates="user", cascade="all, delete-orphan")


class PantryItem(Base):
    __tablename__ = "pantry_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)

    name = Column(String(120), nullable=False)
    category = Column(String(60), nullable=True)
    quantity = Column(Integer, default=1)
    unit = Column(String(20), nullable=True)
    expiry_date = Column(Date, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="pantry_items")


class ShoppingList(Base):
    __tablename__ = "shopping_lists"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)

    name = Column(String(120), nullable=False)
    items_json = Column(Text, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="shopping_lists")


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)

    page = Column(String(32), nullable=False)   # "recommend" | "quickgen"
    rating = Column(Integer, nullable=False)    # 1..5
    comment = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="feedback_entries")