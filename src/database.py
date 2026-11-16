from sqlalchemy.orm import sessionmaker
from src.models import get_engine

engine = get_engine()
SessionLocal = sessionmaker(bind = engine, autocommit = False, autoflush=False)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
