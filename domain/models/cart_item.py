from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB

from domain.models.base import Base  

class CartItem(Base):
    __tablename__ = "cart_items"

    item_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.user_id"), index=True, nullable=False)
    product_id: Mapped[str] = mapped_column(String, index=True, nullable=False)

    analysis_snapshot: Mapped[dict | None] = mapped_column(JSONB, nullable=True)