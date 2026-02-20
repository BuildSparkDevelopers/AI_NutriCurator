from __future__ import annotations

from datetime import datetime
from sqlalchemy import Integer, String, Boolean, DateTime, func, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from domain.models.base import Base


class Product(Base):
    __tablename__ = "products"
    __table_args__ = (
        UniqueConstraint("brand", name="uq_products_brand"),  # 너 스펙 그대로
    )

    product_id: Mapped[int] = mapped_column(Integer, primary_key=True)

    name: Mapped[str] = mapped_column(String, nullable=False)
    brand: Mapped[str] = mapped_column(String, nullable=False)

    category_id: Mapped[int | None] = mapped_column(Integer, nullable=True)  # FK는 다음 단계에

    image_url: Mapped[str | None] = mapped_column(String, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    rawmtrl: Mapped[str | None] = mapped_column(Text, nullable=True)
    allergymtrl: Mapped[str | None] = mapped_column(Text, nullable=True)

    kcal: Mapped[int | None] = mapped_column(Integer, nullable=True)
    protein_g: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fat_g: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ash_g: Mapped[int | None] = mapped_column(Integer, nullable=True)
    carb_g: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sugar_g: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sodium_mg: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cholesterol_mg: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sat_fat_g: Mapped[int | None] = mapped_column(Integer, nullable=True)
    trans_fat_g: Mapped[int | None] = mapped_column(Integer, nullable=True)

    nutrient_basis_g: Mapped[int | None] = mapped_column(Integer, nullable=True)
    serving_ref_g: Mapped[int | None] = mapped_column(Integer, nullable=True)
    food_weight_g: Mapped[int | None] = mapped_column(Integer, nullable=True)

    gi: Mapped[int | None] = mapped_column(Integer, nullable=True)
    gl: Mapped[int | None] = mapped_column(Integer, nullable=True)