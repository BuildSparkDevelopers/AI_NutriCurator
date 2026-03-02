import enum
from sqlalchemy import (
    String, Integer, ForeignKey, Date, Enum, Numeric, Text
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from domain.models.base import Base



# Enums (DB에 들어갈 "값")
class Gender(enum.Enum):
    M = "M"
    F = "F"

class Diabetes(enum.Enum):
    type1 = "type1"
    type2 = "type2"
    pre_type1 = "pre_type1"
    pre_type2 = "pre_type2"
    na = "na"

class Hypertension(enum.Enum):
    prehypertension = "prehypertension"
    stage1 = "stage1"
    stage2 = "stage2"
    na = "na"

class KidneyDisease(enum.Enum):
    CKD_3_5 = "CKD_3_5"
    HD = "HD"
    PD = "PD"
    na = "na"

class Allergy(enum.Enum):
    EGG = "EGG"
    MILK = "MILK"
    BUCKWHEAT = "BUCKWHEAT"
    PEANUT = "PEANUT"
    SOYBEAN = "SOYBEAN"
    WHEAT = "WHEAT"
    MACKEREL = "MACKEREL"
    CRAB = "CRAB"
    SHRIMP = "SHRIMP"
    PORK = "PORK"
    PEACH = "PEACH"
    TOMATO = "TOMATO"
    SULFITE = "SULFITE"
    WALNUT = "WALNUT"
    CHICKEN = "CHICKEN"
    BEEF = "BEEF"
    SQUID = "SQUID"
    PINE_NUT = "PINE_NUT"
    SEASAME = "SEASAME"
    ALMOND = "ALMOND"
    OYSTER = "OYSTER"
    ABALONE = "ABALONE"
    MUSSEL = "MUSSEL"



# Table

class UserHealthProfile(Base):
    __tablename__ = "user_health_profile"

    # PK + FK (users.user_id)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        primary_key=True,
    )

    gender: Mapped[Gender | None] = mapped_column(Enum(Gender, name="gender"), nullable=True)
    birth_date: Mapped["Date | None"] = mapped_column(Date, nullable=True)

    height: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    weight: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)

    # MVP에서는 저장->"매번 갱신"이면 나중에 분리하는 게 편할 듯 (예: activity_log 테이블 따로)
    average_of_steps: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # 0단계, 1단계, 2단계, ... 5단계
    activity_level: Mapped[int | None] = mapped_column(String(20), nullable=True)

    diabetes: Mapped[Diabetes | None] = mapped_column(Enum(Diabetes, name="diabetes"), nullable=True)
    hypertension: Mapped[Hypertension | None] = mapped_column(Enum(Hypertension, name="hypertension"), nullable=True)
    kidneydisease: Mapped[KidneyDisease | None] = mapped_column(Enum(KidneyDisease, name="kidneydisease"), nullable=True)
    allergy: Mapped[list[Allergy]] = mapped_column(
        ARRAY(Enum(Allergy, name="allergy")),
        nullable=False,
        default=list,
        server_default="{}",
    )

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    favorite: Mapped[str | None] = mapped_column(String(255), nullable=True)
    goal: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # (선택) 관계 - 필요할 때만
    # user = relationship("User", back_populates="health_profile")