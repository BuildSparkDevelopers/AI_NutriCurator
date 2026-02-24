# infra/db/session.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.settings import settings

engine = create_engine(settings.DATABASE_URL, future=True, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)

def get_db():
    """
    FastAPI dependency
    - 요청 들어올 때 세션 열고
    - 요청 끝나면 닫아줌
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_session():
    # 기존 get_db랑 완전 동일 (이름만 맞춰주는 용)
    yield from get_db()