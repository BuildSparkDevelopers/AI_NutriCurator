 # 역할: health_profiles 저장/조회만 담당

from typing import Optional
from infra.db.store import InMemoryStore

class HealthProfileRepository:
    def __init__(self, db: InMemoryStore):
        self.db = db

    def get_by_user_id(self, user_id: int) -> Optional[dict]:
        return self.db.health_profiles.get(user_id)

    def upsert(self, user_id: int, profile: dict) -> dict:
        self.db.health_profiles[user_id] = profile
        return profile
