# 역할: FastAPI Depends로 "DB 세션처럼" STORE 주입
# 나중에 PostgreSQL 붙이면 여기만 SQLAlchemy session으로 교체

from typing import Generator
from infra.db.store import STORE, InMemoryStore

def get_db() -> Generator[InMemoryStore, None, None]:
    yield STORE
