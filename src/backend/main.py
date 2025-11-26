# src/backend/main.py
from __future__ import annotations

from datetime import timedelta
import json
import time
from typing import List

from fastapi import FastAPI, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from . import models, schemas
from .database import engine, Base
from .auth import get_password_hash, authenticate_user, create_access_token
from .deps import get_current_user_dep, get_db_dep

from .services import pantry as pantry_service
from .services import recipes as recipes_service
from .services import shopping as shopping_service

from .metrics import REQUEST_COUNT, REQUEST_LATENCY, IN_PROGRESS, USAGE_COUNT, FEEDBACK_COUNT

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AppetIte Backend", version="0.3.0")


@app.middleware("http")
async def prometheus_middleware(request: Request, call_next):
    start_time = time.time()
    IN_PROGRESS.inc()
    response = None
    status_code = 500
    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    finally:
        IN_PROGRESS.dec()
        REQUEST_LATENCY.labels(endpoint=request.url.path).observe(time.time() - start_time)
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status_code=str(status_code),
        ).inc()


@app.get("/metrics")
def metrics():
    return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)


# ---------- Auth ----------
@app.post("/signup", response_model=schemas.UserRead, status_code=201)
def signup(user_in: schemas.UserCreate, db: Session = Depends(get_db_dep)):
    existing = (
        db.query(models.User)
        .filter(
            (models.User.username == user_in.username)
            | (models.User.email == user_in.email)
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Username or email already exists")

    user = models.User(
        username=user_in.username.strip(),
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db_dep)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=60 * 24),
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/me", response_model=schemas.UserRead)
def read_me(current_user: models.User = Depends(get_current_user_dep)):
    return current_user


# ---------- Pantry ----------
@app.post("/pantry/", response_model=schemas.PantryItemRead, status_code=201)
def add_pantry_item(
    item_in: schemas.PantryItemCreate,
    db: Session = Depends(get_db_dep),
    current_user: models.User = Depends(get_current_user_dep),
):
    USAGE_COUNT.labels(feature="pantry_add").inc()
    return pantry_service.create_pantry_item(db, current_user.id, item_in)


@app.get("/pantry/", response_model=List[schemas.PantryItemRead])
def list_pantry(
    db: Session = Depends(get_db_dep),
    current_user: models.User = Depends(get_current_user_dep),
):
    USAGE_COUNT.labels(feature="pantry_list").inc()
    return pantry_service.list_pantry_items(db, current_user.id)


@app.delete("/pantry/{item_id}", status_code=204)
def delete_pantry(
    item_id: int,
    db: Session = Depends(get_db_dep),
    current_user: models.User = Depends(get_current_user_dep),
):
    USAGE_COUNT.labels(feature="pantry_delete").inc()
    pantry_service.delete_pantry_item(db, current_user.id, item_id)
    return Response(status_code=204)


# ---------- Recommend ----------
@app.post("/recommend", response_model=List[schemas.Recipe])
def recommend(
    req: schemas.RecommendationRequest,
    db: Session = Depends(get_db_dep),
    current_user: models.User = Depends(get_current_user_dep),
):
    USAGE_COUNT.labels(feature="recommend").inc()

    # If user typed ingredients → use them
    if req.ingredients:
        ing = req.ingredients

    # Otherwise use pantry ingredients
    else:
        pantry_items = pantry_service.list_pantry_items(db, current_user.id)
        ing = [item.name for item in pantry_items]

    # Generate ONE recommended recipe
    results = recipes_service.recommend_recipes(
        ingredients=ing,
        category=req.category,
        num_recipes=1,
    )

    return results


# ---------- Quick Generate ----------
@app.post("/quick-generate", response_model=schemas.QuickGenerateResponse)
def quick_generate(
    req: schemas.QuickGenerateRequest,
    db: Session = Depends(get_db_dep),
    current_user: models.User = Depends(get_current_user_dep),
):
    USAGE_COUNT.labels(feature="quick_generate").inc()

    # Call the model generator correctly
    raw_json = recipes_service.generate_with_model(
        ingredients=req.ingredients,
        category=req.category,
        mode="quick",
    )

    try:
        recipe_dict = json.loads(raw_json)
    except:
        recipe_dict = {
            "title": "Quick Recipe",
            "ingredients": req.ingredients,
            "instructions": raw_json,
            "category": req.category,
        }

    recipe = schemas.Recipe(
        title=recipe_dict.get("title", "Quick Recipe"),
        ingredients=recipe_dict.get("ingredients", req.ingredients),
        instructions=recipe_dict.get("instructions", ""),
        category=req.category,
    )

    return schemas.QuickGenerateResponse(recipe=recipe)


# ---------- Shopping List ----------
@app.post("/shopping-list", status_code=201)
def create_shopping_list(
    req: schemas.ShoppingListCreate,
    db: Session = Depends(get_db_dep),
    current_user: models.User = Depends(get_current_user_dep),
):
    """
    Creates missing-ingredients shopping list and persists it.
    Response matches frontend expectation:
        { recipe_name, items }
    """
    pantry = pantry_service.list_pantry_items(db, current_user.id)
    missing = shopping_service.compute_shopping_list_items(req.items, pantry)

    sl = models.ShoppingList(
        user_id=current_user.id,
        name=req.name.strip(),
        items_json=json.dumps(missing),
    )
    db.add(sl)
    db.commit()
    db.refresh(sl)

    return {
        "id": sl.id,
        "recipe_name": sl.name,
        "items": missing,
        "created_at": sl.created_at,
    }


@app.get("/shopping-list", response_model=List[schemas.ShoppingListRead])
def list_shopping_lists(
    db: Session = Depends(get_db_dep),
    current_user: models.User = Depends(get_current_user_dep),
):
    lists = (
        db.query(models.ShoppingList)
        .filter(models.ShoppingList.user_id == current_user.id)
        .order_by(models.ShoppingList.created_at.desc())
        .all()
    )

    out = []
    for sl in lists:
        out.append(
            schemas.ShoppingListRead(
                id=sl.id,
                user_id=sl.user_id,
                name=sl.name,
                items=json.loads(sl.items_json),
                created_at=sl.created_at,
            )
        )
    return out
# ---------- Cook ----------
@app.post("/cook", response_model=schemas.CookResponse)
def cook(
    req: schemas.CookRequest,
    db: Session = Depends(get_db_dep),
    current_user: models.User = Depends(get_current_user_dep),
):
    """
    Remove ingredients that were used in a cooked recipe from the user's pantry.
    """
    USAGE_COUNT.labels(feature="cook").inc()

    removed = pantry_service.remove_used_items(
        db=db,
        user_id=current_user.id,
        used=req.ingredients,
    )

    return schemas.CookResponse(removed=removed)

# ---------- Feedback ----------
@app.post("/feedback", status_code=201)
def add_feedback(
    req: schemas.FeedbackCreate,
    db: Session = Depends(get_db_dep),
    current_user: models.User = Depends(get_current_user_dep),
):
    FEEDBACK_COUNT.labels(page=req.page, rating=str(req.rating)).inc()
    USAGE_COUNT.labels(feature="feedback").inc()

    fb = models.Feedback(
        user_id=current_user.id,
        page=req.page,
        rating=req.rating,
        comment=req.comment,
    )
    db.add(fb)
    db.commit()

    return {"status": "ok"}


@app.get("/health")
def health_check():
    return {"status": "ok"}