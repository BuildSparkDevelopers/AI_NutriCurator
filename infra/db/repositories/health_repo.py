from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from domain.models.user_health_profile import UserHealthProfile

# ✅ 지금 \d+로 확인된 컬럼들만 일단 반영
PROFILE_FIELDS = {
    "gender",
    "birth_date",
    "height",
    "weight",
    "average_of_steps",
    "activity_level",
    "diabetes",
}

class HealthProfileRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_user_id(self, user_id: int) -> Optional[dict]:
        stmt = select(UserHealthProfile).where(UserHealthProfile.user_id == user_id)
        row = self.db.execute(stmt).scalar_one_or_none()
        if row is None:
            return None
        return {k: getattr(row, k) for k in PROFILE_FIELDS}

    def upsert(self, user_id: int, profile: dict) -> dict:
        payload = {k: v for k, v in profile.items() if k in PROFILE_FIELDS}

        stmt = select(UserHealthProfile).where(UserHealthProfile.user_id == user_id)
        row = self.db.execute(stmt).scalar_one_or_none()

        if row is None:
            row = UserHealthProfile(user_id=user_id, **payload)
            self.db.add(row)
        else:
            for k, v in payload.items():
                setattr(row, k, v)

        self.db.commit()
        return {k: getattr(row, k) for k in PROFILE_FIELDS}