from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Use psycopg (v3) driver
engine = create_engine(settings.DATABASE_URL.replace("postgresql://", "postgresql+psycopg://"))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()