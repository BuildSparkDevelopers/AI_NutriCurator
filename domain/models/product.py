from __future__ import annotations

from datetime import datetime
from sqlalchemy import Integer, String, Boolean, DateTime, func, Text, UniqueConstraint,Float
from sqlalchemy.orm import Mapped, mapped_column
from domain.models.base import Base


class Product(Base):
    __tablename__ = "products"
    __table_args__ = (
        UniqueConstraint("brand", name="uq_products_brand"),  # ERD 스펙 그대로
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

    kcal: Mapped[float | None] = mapped_column(Float, nullable=True)
    protein_g: Mapped[float | None] = mapped_column(Float, nullable=True)
    fat_g: Mapped[float | None] = mapped_column(Float, nullable=True)
    ash_g: Mapped[float | None] = mapped_column(Float, nullable=True)
    carb_g: Mapped[float | None] = mapped_column(Float, nullable=True)
    sugar_g: Mapped[float | None] = mapped_column(Float, nullable=True)
    sodium_mg: Mapped[float | None] = mapped_column(Float, nullable=True)
    cholesterol_mg: Mapped[float | None] = mapped_column(Float, nullable=True)
    sat_fat_g: Mapped[float | None] = mapped_column(Float, nullable=True)
    trans_fat_g: Mapped[float | None] = mapped_column(Float, nullable=True)

    nutrient_basis_g: Mapped[float | None] = mapped_column(Float, nullable=True)
    serving_ref_g: Mapped[float | None] = mapped_column(Float, nullable=True)
    food_weight_g: Mapped[float | None] = mapped_column(Float, nullable=True)

    gi: Mapped[float | None] = mapped_column(Float, nullable=True)
    gl: Mapped[float | None] = mapped_column(Float, nullable=True)