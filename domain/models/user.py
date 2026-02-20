# domain/models/user.py
from __future__ import annotations

from sqlalchemy import (
    Boolean,
    Integer,
    String,
    TIMESTAMP,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from domain.models.base import Base


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    # Postgres TIMESTAMPTZ = TIMESTAMP(timezone=True)
    created_at: Mapped[object] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    updated_at: Mapped[object] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    is_sensitive_agreed: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))

    agreed_at: Mapped[object | None] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
    )

    # 필수 동의 2종
    is_tos_agreed: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    is_privacy_agreed: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))