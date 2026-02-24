from __future__ import annotations

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from domain.models.base import Base


class Nutrient(Base):
    __tablename__ = "nutrients"

    nutri_id: Mapped[int] = mapped_column(Integer, primary_key=True)

    name: Mapped[str] = mapped_column(String, nullable=False)
    name_en: Mapped[str | None] = mapped_column(String, nullable=True)
    unit: Mapped[str | None] = mapped_column(String, nullable=True)

    # 1/0 방식 bool
    is_mandatory_display: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    diabetes_risk: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    hypertension_risk: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    is_glycemic_factor: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    kidneydisease_risk: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")