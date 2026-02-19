from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.settings import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    # FastAPI dependency로 쓰기 좋게: 요청이 끝나면 세션을 닫아줌
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()    
