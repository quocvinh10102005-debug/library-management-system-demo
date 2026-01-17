from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base



class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)

    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # "member" | "librarian"
    role = Column(String, default="member", nullable=False)

    library_card_id = Column(String, unique=True, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    borrows = relationship("Borrow", back_populates="user")
    reservations = relationship("Reservation", back_populates="user")
    feedbacks = relationship("Feedback", back_populates="user")
    payments = relationship("Payment", back_populates="user")


class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True)

    title = Column(String, index=True, nullable=False)
    author = Column(String, index=True, nullable=False)
    isbn = Column(String, unique=True, index=True, nullable=True)

    total_copies = Column(Integer, default=1, nullable=False)
    available_copies = Column(Integer, default=1, nullable=False)

    borrows = relationship("Borrow", back_populates="book")
    reservations = relationship("Reservation", back_populates="book")


class Reservation(Base):
    __tablename__ = "reservations"
    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)

    # "pending" | "cancelled" | "fulfilled"
    status = Column(String, default="pending", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="reservations")
    book = relationship("Book", back_populates="reservations")


class Borrow(Base):
    __tablename__ = "borrows"
    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)

    issued_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    due_at = Column(DateTime, nullable=False)
    returned_at = Column(DateTime, nullable=True)

    renewed_count = Column(Integer, default=0, nullable=False)

    # fine stored per borrow (calculated on return)
    fine_cents = Column(Integer, default=0, nullable=False)

    user = relationship("User", back_populates="borrows")
    book = relationship("Book", back_populates="borrows")


class Feedback(Base):
    __tablename__ = "feedbacks"
    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="feedbacks")


class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount_cents = Column(Integer, nullable=False)
    reason = Column(String, default="fine", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="payments")

