from __future__ import annotations

from datetime import datetime
from sqlalchemy import Integer, String, Boolean, DateTime, func, Text, Float
from sqlalchemy.orm import Mapped, mapped_column
from domain.models.base import Base


class Product(Base):
    __tablename__ = "products"

    product_id: Mapped[int] = mapped_column(Integer, primary_key=True)

    name: Mapped[str] = mapped_column(Text, nullable=False)
    brand: Mapped[str] = mapped_column(Text, nullable=False)

    # products.category_id is currently text in DB
    category_id: Mapped[str | None] = mapped_column(Text, nullable=True)

    image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[int | None] = mapped_column(Integer, nullable=True)

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

    # Map ORM attribute names used by services to real DB column names
    kcal: Mapped[float | None] = mapped_column("energy", Float, nullable=True)
    protein_g: Mapped[float | None] = mapped_column("protein", Float, nullable=True)
    fat_g: Mapped[float | None] = mapped_column("fat", Float, nullable=True)
    ash_g: Mapped[float | None] = mapped_column("mineral", Float, nullable=True)
    carb_g: Mapped[float | None] = mapped_column("carbohydrate", Float, nullable=True)
    sugar_g: Mapped[float | None] = mapped_column("sugar", Float, nullable=True)
    sodium_mg: Mapped[float | None] = mapped_column("sodium", Float, nullable=True)
    cholesterol_mg: Mapped[float | None] = mapped_column("cholesterol", Float, nullable=True)
    sat_fat_g: Mapped[float | None] = mapped_column("saturated_fat", Float, nullable=True)
    trans_fat_g: Mapped[float | None] = mapped_column("trans_fat", Float, nullable=True)

    nutrient_basis_g: Mapped[str | None] = mapped_column("serving_size_g", Text, nullable=True)
    serving_ref_g: Mapped[str | None] = mapped_column("suggested_intake_g", Text, nullable=True)
    food_weight_g: Mapped[str | None] = mapped_column("total_weight_g", Text, nullable=True)

    gi: Mapped[float | None] = mapped_column(Float, nullable=True)
    gl: Mapped[float | None] = mapped_column(Float, nullable=True)