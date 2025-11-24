from __future__ import annotations

from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException

from .. import models, schemas


def create_pantry_item(db: Session, user_id: int, item_in: schemas.PantryItemCreate):
    obj = models.PantryItem(
        user_id=user_id,
        name=item_in.name.strip(),
        quantity=item_in.quantity,
        unit=item_in.unit,
        expiry_date=item_in.expiry_date,
        category=item_in.category,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def list_pantry_items(db: Session, user_id: int) -> List[models.PantryItem]:
    return (
        db.query(models.PantryItem)
        .filter(models.PantryItem.user_id == user_id)
        .order_by(models.PantryItem.created_at.desc())
        .all()
    )


def delete_pantry_item(db: Session, user_id: int, item_id: int):
    item = (
        db.query(models.PantryItem)
        .filter(
            models.PantryItem.id == item_id,
            models.PantryItem.user_id == user_id,
        )
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(item)
    db.commit()


def remove_used_items(db: Session, user_id: int, used: List[str]) -> List[str]:
    removed = []
    used_lower = {u.strip().lower() for u in used}

    items = (
        db.query(models.PantryItem)
        .filter(models.PantryItem.user_id == user_id)
        .all()
    )

    for it in items:
        if it.name.lower() in used_lower:
            removed.append(it.name)
            db.delete(it)

    db.commit()
    return removed