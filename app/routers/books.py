from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/books", tags=["Books"])


@router.get("/", response_model=list[schemas.BookOut])
def list_books(db: Session = Depends(get_db)):
    return db.query(models.Book).order_by(models.Book.id.desc()).all()


@router.get("/search", response_model=list[schemas.BookOut])
def search_books(q: str, db: Session = Depends(get_db)):
    pattern = f"%{q.strip()}%"
    return (
        db.query(models.Book)
        .filter(or_(models.Book.title.like(pattern), models.Book.author.like(pattern), models.Book.isbn.like(pattern)))
        .all()
    )
