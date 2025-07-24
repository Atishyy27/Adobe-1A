# Backend/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Use a simple SQLite database for now to avoid connection issues.
# This will create a file named "hackathon.db" in your root folder.
DATABASE_URL = "sqlite:///./hackathon.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()