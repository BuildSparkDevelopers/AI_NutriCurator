# infra/db/adapters/agent_adapter.py
from __future__ import annotations

from typing import Any, Dict, List, Optional, Iterable
from sqlalchemy.orm import Session
from sqlalchemy import select

# ✅ 너희 ORM 모델 경로에 맞춰 import 경로만 조정하면 됨
from domain.models.product import Product
from domain.models.user_health_profile import UserHealthProfile
from domain.models.cart_item import CartItem


class AgentDBAdapter:
    """
    ✅ DB(Session) -> agent가 쓰던 dict/json 포맷으로 공급하는 단일 어댑터.

    - agent는 "dict/json"만 받는다 (기존 유지)
    - 이 어댑터가 DB에서 조회해서 dict로 변환해준다.
    """

    def __init__(self, db: Session):
        self.db = db

    # -------------------------
    # 공통: ORM -> dict 변환
    # -------------------------
    @staticmethod
    def to_dict(obj: Any, *, include: Optional[Iterable[str]] = None) -> Dict[str, Any]:
        """
        SQLAlchemy ORM 객체 -> dict
        include: 특정 컬럼만 포함하고 싶을 때
        """
        if obj is None:
            return {}

        include_set = set(include) if include else None
        data: Dict[str, Any] = {}
        for col in obj.__table__.columns:
            key = col.name
            if include_set and key not in include_set:
                continue
            data[key] = getattr(obj, key)
        return data

    # -------------------------
    # Products: agent용 dict 공급
    # -------------------------
    def get_product(self, product_id: int) -> Optional[Dict[str, Any]]:
        stmt = select(Product).where(Product.product_id == product_id)
        obj = self.db.execute(stmt).scalar_one_or_none()
        return self.to_dict(obj) if obj else None

    def get_products_map(
        self,
        *,
        limit: int = 20000,
        offset: int = 0,
        include: Optional[Iterable[str]] = None,
    ) -> Dict[int, Dict[str, Any]]:
        """
        agent가 예전처럼 쓰던 형태:
        {
          1: {product dict...},
          2: {product dict...},
        }
        """
        stmt = select(Product).limit(limit).offset(offset)
        rows = self.db.execute(stmt).scalars().all()
        return {p.product_id: self.to_dict(p, include=include) for p in rows}

    def search_products_map(
        self,
        *,
        q: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 5000,
        offset: int = 0,
        include: Optional[Iterable[str]] = None,
    ) -> Dict[int, Dict[str, Any]]:
        """
        agent 입력을 줄이려고, 서버에서 후보를 줄여서 dict로 공급하는 버전.
        """
        stmt = select(Product)

        if category:
            stmt = stmt.where(Product.category == category)
        if q:
            like = f"%{q.strip()}%"
            stmt = stmt.where(Product.name.ilike(like) | Product.brand.ilike(like))

        stmt = stmt.limit(limit).offset(offset)
        rows = self.db.execute(stmt).scalars().all()
        return {p.product_id: self.to_dict(p, include=include) for p in rows}

    # -------------------------
    # User Health Profile: dict
    # -------------------------
    def get_user_health_profile(self, user_id: int) -> Dict[str, Any]:
        stmt = select(UserHealthProfile).where(UserHealthProfile.user_id == user_id)
        obj = self.db.execute(stmt).scalar_one_or_none()
        return self.to_dict(obj) if obj else {}

    # -------------------------
    # Cart Items: dict list
    # -------------------------
    def list_cart_items(self, user_id: int) -> List[Dict[str, Any]]:
        stmt = (
            select(CartItem)
            .where(CartItem.user_id == user_id)
            .order_by(CartItem.item_id.desc())
        )
        items = self.db.execute(stmt).scalars().all()
        return [self.to_dict(it) for it in items]

    # -------------------------
    # Agent 입력 payload 만들기(선택)
    # -------------------------
    def build_agent_payload(
        self,
        *,
        user_id: int,
        q: Optional[str] = None,
        category: Optional[str] = None,
        product_limit: int = 5000,
        include_product_fields: Optional[Iterable[str]] = None,
    ) -> Dict[str, Any]:
        """
        agent가 받기 좋은 "한 덩어리 payload"를 만들어줌.
        """
        profile = self.get_user_health_profile(user_id)
        products = self.search_products_map(
            q=q,
            category=category,
            limit=product_limit,
            include=include_product_fields,
        )
        cart_items = self.list_cart_items(user_id)

        return {
            "user": {"user_id": user_id, "health_profile": profile},
            "products": products,         # Dict[int, dict]
            "cart_items": cart_items,     # List[dict]
            "query": {"q": q, "category": category},
        }