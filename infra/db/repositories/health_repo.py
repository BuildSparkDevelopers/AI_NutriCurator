from enum import Enum
from typing import Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from domain.models.user_health_profile import UserHealthProfile, Allergy

# ✅ 지금 \d+로 확인된 컬럼들만 일단 반영
PROFILE_FIELDS = {
    "gender",
    "birth_date",
    "height",
    "weight",
    "average_of_steps",
    "activity_level",
    "diabetes",
    "hypertension",
    "kidneydisease",
    "allergy",
    "notes",
    "favorite",
    "goal",
}

class HealthProfileRepository:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _serialize_value(value: Any) -> Any:
        if isinstance(value, Enum):
            return value.value
        if isinstance(value, list):
            return [v.value if isinstance(v, Enum) else v for v in value]
        return value

    @staticmethod
    def _normalize_allergy_value(raw: Any) -> list[Allergy]:
        if raw is None:
            return []

        values: list[str] = []
        if isinstance(raw, str):
            values = [part.strip().upper() for part in raw.split(",") if part.strip()]
        elif isinstance(raw, list):
            for item in raw:
                if isinstance(item, Allergy):
                    values.append(item.value)
                elif isinstance(item, str):
                    txt = item.strip().upper()
                    if txt:
                        values.append(txt)
        else:
            return []

        normalized: list[Allergy] = []
        for item in values:
            try:
                normalized.append(Allergy(item))
            except ValueError:
                continue
        return normalized

    def get_by_user_id(self, user_id: int) -> Optional[dict]:
        stmt = select(UserHealthProfile).where(UserHealthProfile.user_id == user_id)
        row = self.db.execute(stmt).scalar_one_or_none()
        if row is None:
            return None
        return {k: self._serialize_value(getattr(row, k)) for k in PROFILE_FIELDS}

    def upsert(self, user_id: int, profile: dict) -> dict:
        payload = {k: v for k, v in profile.items() if k in PROFILE_FIELDS}
        if "allergy" in payload:
            payload["allergy"] = self._normalize_allergy_value(payload["allergy"])

        stmt = select(UserHealthProfile).where(UserHealthProfile.user_id == user_id)
        row = self.db.execute(stmt).scalar_one_or_none()

        if row is None:
            row = UserHealthProfile(user_id=user_id, **payload)
            self.db.add(row)
        else:
            for k, v in payload.items():
                setattr(row, k, v)

        self.db.commit()
        return {k: self._serialize_value(getattr(row, k)) for k in PROFILE_FIELDS}