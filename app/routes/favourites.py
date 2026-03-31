from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Favorite

router = APIRouter()

# DB connection
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ⭐ Add Favorite
@router.post("/favorites/{user_id}/{city_id}")
def add_favorite(user_id: int, city_id: int, db: Session = Depends(get_db)):

    existing = db.query(Favorite).filter(
        Favorite.user_id == user_id,
        Favorite.city_id == city_id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Already in favorites")

    fav = Favorite(user_id=user_id, city_id=city_id)
    db.add(fav)
    db.commit()

    return {"message": "Added to favorites"}


# ⭐ Get Favorites
@router.get("/favorites/{user_id}")
def get_favorites(user_id: int, db: Session = Depends(get_db)):
    return db.query(Favorite).filter(Favorite.user_id == user_id).all()


# ⭐ Remove Favorite
@router.delete("/favorites/{user_id}/{city_id}")
def remove_favorite(user_id: int, city_id: int, db: Session = Depends(get_db)):

    fav = db.query(Favorite).filter(
        Favorite.user_id == user_id,
        Favorite.city_id == city_id
    ).first()

    if not fav:
        raise HTTPException(status_code=404, detail="Not found")

    db.delete(fav)
    db.commit()

    return {"message": "Removed from favorites"}