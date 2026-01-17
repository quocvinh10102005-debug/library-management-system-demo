from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: str
    library_card_id: Optional[str] = None

    class Config:
        from_attributes = True


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class BookCreate(BaseModel):
    title: str
    author: str
    isbn: Optional[str] = None
    total_copies: int = Field(ge=1, default=1)


class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    isbn: Optional[str] = None
    total_copies: Optional[int] = Field(default=None, ge=1)
    available_copies: Optional[int] = Field(default=None, ge=0)


class BookOut(BaseModel):
    id: int
    title: str
    author: str
    isbn: Optional[str] = None
    total_copies: int
    available_copies: int

    class Config:
        from_attributes = True


class ReservationCreate(BaseModel):
    book_id: int


class ReservationOut(BaseModel):
    id: int
    user_id: int
    book_id: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class BorrowIssueIn(BaseModel):
    book_id: int
    days: int = Field(default=14, ge=1, le=60)


class BorrowOut(BaseModel):
    id: int
    user_id: int
    book_id: int
    issued_at: datetime
    due_at: datetime
    returned_at: Optional[datetime] = None
    renewed_count: int
    fine_cents: int

    class Config:
        from_attributes = True


class BorrowWithBookOut(BaseModel):
    borrow: BorrowOut
    book: BookOut


class FeedbackCreate(BaseModel):
    message: str


class FeedbackOut(BaseModel):
    id: int
    user_id: int
    message: str
    created_at: datetime

    class Config:
        from_attributes = True


class PaymentCreate(BaseModel):
    amount_cents: int = Field(ge=1)
    reason: str = "fine"


class PaymentOut(BaseModel):
    id: int
    user_id: int
    amount_cents: int
    reason: str
    created_at: datetime

    class Config:
        from_attributes = True


class MemberUpdate(BaseModel):
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
from pydantic import BaseModel

class RoleUpdate(BaseModel):
    role: str  # "member" or "librarian"
