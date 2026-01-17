from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.database import get_db
from app import models, schemas
from app.routers.auth import get_current_user

router = APIRouter(prefix="/member", tags=["Member (User)"])

FINE_PER_LATE_DAY_CENTS = 1000
MAX_RENEW = 1


def _outstanding_fine_cents(db: Session, user_id: int) -> int:
    borrows = db.query(models.Borrow).filter(models.Borrow.user_id == user_id).all()
    total_fines = sum(b.fine_cents for b in borrows)
    payments = db.query(models.Payment).filter(models.Payment.user_id == user_id).all()
    total_paid = sum(p.amount_cents for p in payments)
    return max(0, total_fines - total_paid)


@router.post("/reservations", response_model=schemas.ReservationOut)
def reserve_book(payload: schemas.ReservationCreate, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    book = db.query(models.Book).filter(models.Book.id == payload.book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    existing = (
        db.query(models.Reservation)
        .filter(models.Reservation.user_id == user.id, models.Reservation.book_id == book.id, models.Reservation.status == "pending")
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Already reserved")

    res = models.Reservation(user_id=user.id, book_id=book.id, status="pending")
    db.add(res)
    db.commit()
    db.refresh(res)
    return res


@router.post("/borrows/issue", response_model=schemas.BorrowOut)
def issue_book(payload: schemas.BorrowIssueIn, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    if not user.library_card_id:
        raise HTTPException(status_code=400, detail="No library card. Ask librarian to issue a library card.")

    book = db.query(models.Book).filter(models.Book.id == payload.book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if book.available_copies <= 0:
        raise HTTPException(status_code=400, detail="No available copies")

    # If user has a pending reservation, mark fulfilled
    res = (
        db.query(models.Reservation)
        .filter(models.Reservation.user_id == user.id, models.Reservation.book_id == book.id, models.Reservation.status == "pending")
        .first()
    )
    if res:
        res.status = "fulfilled"

    due = datetime.utcnow() + timedelta(days=payload.days)
    borrow = models.Borrow(user_id=user.id, book_id=book.id, due_at=due)

    book.available_copies -= 1

    db.add(borrow)
    db.commit()
    db.refresh(borrow)
    return borrow


@router.post("/borrows/{borrow_id}/return", response_model=schemas.BorrowOut)
def return_book(borrow_id: int, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    borrow = db.query(models.Borrow).filter(models.Borrow.id == borrow_id, models.Borrow.user_id == user.id).first()
    if not borrow:
        raise HTTPException(status_code=404, detail="Borrow record not found")
    if borrow.returned_at:
        raise HTTPException(status_code=400, detail="Already returned")

    borrow.returned_at = datetime.utcnow()

    # restore stock
    book = db.query(models.Book).filter(models.Book.id == borrow.book_id).first()
    if book:
        book.available_copies += 1

    # fine if late
    if borrow.returned_at > borrow.due_at:
        days_late = (borrow.returned_at.date() - borrow.due_at.date()).days
        borrow.fine_cents = max(0, days_late) * FINE_PER_LATE_DAY_CENTS

    db.commit()
    db.refresh(borrow)
    return borrow


@router.post("/borrows/{borrow_id}/renew", response_model=schemas.BorrowOut)
def renew_book(borrow_id: int, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    borrow = db.query(models.Borrow).filter(models.Borrow.id == borrow_id, models.Borrow.user_id == user.id).first()
    if not borrow:
        raise HTTPException(status_code=404, detail="Borrow record not found")

    if borrow.returned_at:
        # invalid renewal (as in diagram)
        raise HTTPException(status_code=400, detail="Invalid renewal: already returned")

    if borrow.renewed_count >= MAX_RENEW:
        raise HTTPException(status_code=400, detail="Invalid renewal: renewal limit reached")

    # reject renew if outstanding fine exists
    if _outstanding_fine_cents(db, user.id) > 0:
        raise HTTPException(status_code=400, detail="Invalid renewal: outstanding fine")

    borrow.due_at = borrow.due_at + timedelta(days=7)
    borrow.renewed_count += 1

    db.commit()
    db.refresh(borrow)
    return borrow


@router.get("/borrows", response_model=list[schemas.BorrowWithBookOut])
def my_borrows(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    rows = db.query(models.Borrow).filter(models.Borrow.user_id == user.id).order_by(models.Borrow.id.desc()).all()
    result = []
    for b in rows:
        book = db.query(models.Book).filter(models.Book.id == b.book_id).first()
        result.append({"borrow": b, "book": book})
    return result


@router.post("/payments", response_model=schemas.PaymentOut)
def pay_fine(payload: schemas.PaymentCreate, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    outstanding = _outstanding_fine_cents(db, user.id)
    if outstanding <= 0:
        raise HTTPException(status_code=400, detail="No outstanding fine")

    if payload.amount_cents > outstanding:
        raise HTTPException(status_code=400, detail="Amount exceeds outstanding fine")

    p = models.Payment(user_id=user.id, amount_cents=payload.amount_cents, reason=payload.reason)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@router.post("/feedback", response_model=schemas.FeedbackOut)
def feedback(payload: schemas.FeedbackCreate, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    fb = models.Feedback(user_id=user.id, message=payload.message)
    db.add(fb)
    db.commit()
    db.refresh(fb)
    return fb
