 # 역할: 내 프로필 저장/조회 스키마(MVP: optional 위주)

from typing import Optional
from pydantic import BaseModel

class HealthProfileUpsertRequest(BaseModel):
    gender: Optional[str] = None
    birth_date: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None

    diabetes: Optional[str] = None
    hypertension: Optional[str] = None
    kidneydisease: Optional[str] = None
    allergy: Optional[str] = None

    favorite: Optional[str] = None
    goal: Optional[str] = None
    notes: Optional[str] = None

class HealthProfileResponse(BaseModel):
    user_id: int
    profile: dict
