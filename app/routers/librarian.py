from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import secrets

from app.database import get_db
from app import models, schemas
from app.routers.auth import require_librarian
from app.security import hash_password

router = APIRouter(prefix="/librarian", tags=["Librarian"])


@router.post("/books", response_model=schemas.BookOut)
def add_book(payload: schemas.BookCreate, db: Session = Depends(get_db), librarian: models.User = Depends(require_librarian)):
    book = models.Book(
        title=payload.title,
        author=payload.author,
        isbn=payload.isbn,
        total_copies=payload.total_copies,
        available_copies=payload.total_copies,
    )
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


@router.put("/books/{book_id}", response_model=schemas.BookOut)
def update_book(book_id: int, payload: schemas.BookUpdate, db: Session = Depends(get_db), librarian: models.User = Depends(require_librarian)):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    if payload.title is not None:
        book.title = payload.title
    if payload.author is not None:
        book.author = payload.author
    if payload.isbn is not None:
        book.isbn = payload.isbn
    if payload.total_copies is not None:
        diff = payload.total_copies - book.total_copies
        book.total_copies = payload.total_copies
        book.available_copies = max(0, book.available_copies + diff)
    if payload.available_copies is not None:
        book.available_copies = payload.available_copies

    db.commit()
    db.refresh(book)
    return book


@router.delete("/books/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db), librarian: models.User = Depends(require_librarian)):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(book)
    db.commit()
    return {"message": "deleted"}


@router.post("/members", response_model=schemas.UserOut)
def add_member(payload: schemas.UserCreate, db: Session = Depends(get_db), librarian: models.User = Depends(require_librarian)):
    exists = db.query(models.User).filter(models.User.email == payload.email).first()
    if exists:
        raise HTTPException(status_code=400, detail="Email already exists")

    u = models.User(
        full_name=payload.full_name,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role="member",
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


@router.put("/members/{user_id}", response_model=schemas.UserOut)
def update_member(user_id: int, payload: schemas.MemberUpdate, db: Session = Depends(get_db), librarian: models.User = Depends(require_librarian)):
    u = db.query(models.User).filter(models.User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="Member not found")

    if payload.full_name is not None:
        u.full_name = payload.full_name
    if payload.is_active is not None:
        u.is_active = payload.is_active

    db.commit()
    db.refresh(u)
    return u


@router.delete("/members/{user_id}")
def delete_member(user_id: int, db: Session = Depends(get_db), librarian: models.User = Depends(require_librarian)):
    u = db.query(models.User).filter(models.User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="Member not found")
    db.delete(u)
    db.commit()
    return {"message": "deleted"}

@router.put("/members/{user_id}/role", response_model=schemas.UserOut)
def update_member_role(
    user_id: int,
    payload: schemas.RoleUpdate,
    db: Session = Depends(get_db),
    librarian: models.User = Depends(require_librarian),
):
    role = payload.role.strip().lower()
    if role not in ["member", "librarian"]:
        raise HTTPException(status_code=400, detail="Invalid role. Use 'member' or 'librarian'.")

    u = db.query(models.User).filter(models.User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")

    u.role = role
    db.commit()
    db.refresh(u)
    return u

@router.post("/members/{user_id}/issue-card", response_model=schemas.UserOut)
def issue_library_card(user_id: int, db: Session = Depends(get_db), librarian: models.User = Depends(require_librarian)):
    u = db.query(models.User).filter(models.User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="Member not found")

    if u.library_card_id:
        return u

    u.library_card_id = f"LC-{secrets.token_hex(4).upper()}"
    db.commit()
    db.refresh(u)
    return u


@router.get("/borrows")
def manage_records_list_borrows(db: Session = Depends(get_db), librarian: models.User = Depends(require_librarian)):
    rows = db.query(models.Borrow).order_by(models.Borrow.id.desc()).all()
    result = []
    for b in rows:
        user = db.query(models.User).filter(models.User.id == b.user_id).first()
        book = db.query(models.Book).filter(models.Book.id == b.book_id).first()
        result.append({
            "borrow_id": b.id,
            "member": {"id": user.id, "full_name": user.full_name, "email": user.email} if user else None,
            "book": {"id": book.id, "title": book.title, "author": book.author} if book else None,
            "issued_at": b.issued_at,
            "due_at": b.due_at,
            "returned_at": b.returned_at,
            "renewed_count": b.renewed_count,
            "fine_cents": b.fine_cents,
        })
    return result
