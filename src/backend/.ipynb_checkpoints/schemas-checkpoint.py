# src/backend/schemas.py
from __future__ import annotations

from typing import Optional, List
from pydantic import BaseModel, EmailStr
from datetime import datetime, date


# ---------------- User ----------------
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        orm_mode = True


# ---------------- Pantry ----------------
class PantryItemCreate(BaseModel):
    name: str
    category: Optional[str] = None
    quantity: int = 1
    unit: Optional[str] = None
    expiry_date: Optional[date] = None


class PantryItemRead(PantryItemCreate):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True


# ---------------- Recipes ----------------
class Recipe(BaseModel):
    title: str
    ingredients: List[str]
    instructions: str
    category: Optional[str] = None


class RecommendationRequest(BaseModel):
    ingredients: Optional[List[str]] = None
    category: Optional[str] = None
    num_recipes: int = 5


class QuickGenerateRequest(BaseModel):
    ingredients: List[str]
    category: Optional[str] = None


class QuickGenerateResponse(BaseModel):
    recipe: Recipe


# ---------------- Shopping ----------------
class ShoppingListCreate(BaseModel):
    name: str
    items: List[str]


class ShoppingListRead(BaseModel):
    id: int
    user_id: int
    name: str
    items: List[str]
    created_at: datetime

    class Config:
        orm_mode = True


# ---------------- Cook ----------------
class CookRequest(BaseModel):
    ingredients: List[str]


class CookResponse(BaseModel):
    removed: List[str]


# ---------------- Feedback ----------------
class FeedbackCreate(BaseModel):
    page: str
    rating: int
    comment: Optional[str] = None