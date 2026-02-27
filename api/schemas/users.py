# 역할: 내 프로필 저장/조회 스키마(MVP: optional 위주)

from typing import Optional, Literal
from pydantic import BaseModel

class HealthProfileUpsertRequest(BaseModel):
    gender: Optional[Literal["M", "F"]] = None
    birth_date: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None

    diabetes: Optional[Literal["type1", "type2", "pre_type1", "pre_type2", "na"]] = None
    hypertension: Optional[Literal["prehypertension", "stage1", "stage2", "na"]] = None
    kidneydisease: Optional[Literal["CKD_3_5", "HD", "PD", "na"]] = None
    allergy: Optional[list[Literal[
        "EGG", "MILK", "BUCKWHEAT", "PEANUT", "SOYBEAN", "WHEAT", "MACKEREL",
        "CRAB", "SHRIMP", "PORK", "PEACH", "TOMATO", "SULFITE", "WALNUT",
        "CHICKEN", "BEEF", "SQUID", "PINE_NUT", "SEASAME", "ALMOND",
        "OYSTER", "ABALONE", "MUSSEL"
    ]]] = None

    favorite: Optional[str] = None
    goal: Optional[str] = None
    notes: Optional[str] = None

class HealthProfileResponse(BaseModel):
    user_id: int
    profile: dict
