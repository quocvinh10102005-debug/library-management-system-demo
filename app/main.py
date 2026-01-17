from fastapi import FastAPI
from app.database import Base, engine, SessionLocal
from app import models
from app.security import hash_password

from app.routers import auth, books, member, librarian

app = FastAPI(title="Library Management System (Demo)",
docs_url = "/docs",
redoc_url = "/redoc",
openapi_url = "/openapi.json",
)
# Create tables
Base.metadata.create_all(bind=engine)

# Seed 1 librarian account (for demo)
def seed_librarian():
    db = SessionLocal()
    try:
        exists = db.query(models.User).filter(models.User.email == "librarian@demo.com").first()
        if not exists:
            u = models.User(
                full_name="Demo Librarian",
                email="librarian@demo.com",
                hashed_password=hash_password("123456"),
                role="librarian",
            )
            db.add(u)
            db.commit()
    finally:
        db.close()

seed_librarian()

app.include_router(auth.router)
app.include_router(books.router)
app.include_router(member.router)
app.include_router(librarian.router)


@app.get("/")
def root():
    return {"message": "LMS API is running. Open /docs for Swagger UI."}
