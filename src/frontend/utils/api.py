# src/frontend/utils/api.py
from __future__ import annotations

from typing import Any, Dict, List, Optional
import os
import requests

BASE_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
TIMEOUT = 60

def _headers(token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _wrap(resp: requests.Response) -> Dict[str, Any]:
    try:
        data = resp.json()
    except Exception:
        data = None
    return {
        "code": resp.status_code,
        "message": resp.text if resp.status_code >= 400 else "ok",
        "data": data,
    }


def _safe_request(fn):
    try:
        return _wrap(fn())
    except requests.exceptions.Timeout:
        return {"code": 408, "message": "Request timeout", "data": None}
    except requests.exceptions.ConnectionError:
        return {"code": 503, "message": "Backend not reachable", "data": None}
    except Exception as e:
        return {"code": 500, "message": str(e), "data": None}


# ---------- Auth ----------
def signup(username: str, email: str, password: str) -> Dict[str, Any]:
    return _safe_request(lambda: requests.post(
        f"{BASE_URL}/signup",
        json={"username": username, "email": email, "password": password},
        timeout=TIMEOUT,
    ))


def login(username: str, password: str) -> Dict[str, Any]:
    return _safe_request(lambda: requests.post(
        f"{BASE_URL}/login",
        data={"username": username, "password": password},
        timeout=TIMEOUT,
    ))


# ---------- Pantry ----------
def add_pantry(token: str, item: Dict[str, Any]) -> Dict[str, Any]:
    return _safe_request(lambda: requests.post(
        f"{BASE_URL}/pantry/",
        json=item,
        headers=_headers(token),
        timeout=TIMEOUT,
    ))


def get_pantry(token: str, category: Optional[str] = None) -> Dict[str, Any]:
    params = {"category": category} if category else None
    return _safe_request(lambda: requests.get(
        f"{BASE_URL}/pantry/",
        params=params,
        headers=_headers(token),
        timeout=TIMEOUT,
    ))


def delete_pantry_item(token: str, item_id: int) -> Dict[str, Any]:
    return _safe_request(lambda: requests.delete(
        f"{BASE_URL}/pantry/{item_id}",
        headers=_headers(token),
        timeout=TIMEOUT,
    ))


# ---------- Recommend / Quick ----------
def get_recommendations(token: str, category: Optional[str] = None) -> Dict[str, Any]:
    payload = {"category": category} if category else {}
    return _safe_request(lambda: requests.post(
        f"{BASE_URL}/recommend",
        json=payload,
        headers=_headers(token),
        timeout=TIMEOUT,
    ))


def quick_generate(token: str, ingredients: List[str], category: Optional[str] = None) -> Dict[str, Any]:
    return _safe_request(lambda: requests.post(
        f"{BASE_URL}/quick-generate",
        json={"ingredients": ingredients, "category": category},
        headers=_headers(token),
        timeout=TIMEOUT,
    ))


def cook_recipe(
    token: str,
    recipe_title: str,
    ingredients: list,
    instructions: Optional[str] = None,
) -> Dict[str, Any]:
    """
    'Cook' a recipe by telling the backend which ingredients were used.

    recipe_title and instructions are kept in the signature so the existing
    Streamlit page does not need to change, but the backend currently only
    needs the list of ingredients to update the pantry.
    """
    return _safe_request(lambda: requests.post(
        f"{BASE_URL}/cook",
        json={"ingredients": ingredients},
        headers=_headers(token),
        timeout=TIMEOUT,
    ))


# ---------- Shopping ----------
def create_shopping_list(token: str, recipe_name: str, ingredients: List[str]) -> Dict[str, Any]:
    return _safe_request(lambda: requests.post(
        f"{BASE_URL}/shopping-list",
        json={"name": recipe_name, "items": ingredients},
        headers=_headers(token),
        timeout=TIMEOUT,
    ))


def get_shopping_lists(token: str) -> Dict[str, Any]:
    return _safe_request(lambda: requests.get(
        f"{BASE_URL}/shopping-list",
        headers=_headers(token),
        timeout=TIMEOUT,
    ))


# ---------- Feedback ----------
def submit_feedback(
    token: str,
    page: str,
    rating: int,
    comment: Optional[str] = None,
) -> Dict[str, Any]:
    return _safe_request(lambda: requests.post(
        f"{BASE_URL}/feedback",
        json={"page": page, "rating": rating, "comment": comment},
        headers=_headers(token),
        timeout=TIMEOUT,
    ))