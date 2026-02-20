from __future__ import annotations

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from domain.models.base import Base


class Category(Base):
    __tablename__ = "categories"

    category_id: Mapped[int] = mapped_column(Integer, primary_key=True)  # 내부 ID
    name: Mapped[str] = mapped_column(String, nullable=False)            # 카테고리명
    supercategory: Mapped[str] = mapped_column(String, nullable=False)   # 음식DB / 가공식품DB