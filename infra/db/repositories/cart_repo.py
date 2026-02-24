
#역할: cart 저장소 접근만 담당 (CRUD/조회)
# - 비즈니스 규칙(중복 처리, 응답 모양)은 service에서 담당

from typing import List, Optional, Dict, Any

from sqlalchemy.orm import Session
from sqlalchemy import select, delete

from domain.models.cart_item import CartItem


class CartRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_items(self, user_id: int) -> List[dict]:
        rows = (
            self.db.execute(
                select(CartItem)
                .where(CartItem.user_id == user_id)
                .order_by(CartItem.item_id.desc())
            )
            .scalars()
            .all()
        )
        return [
            {
                "item_id": r.item_id,
                "user_id": r.user_id,
                "product_id": r.product_id,
                "analysis_snapshot": r.analysis_snapshot,
            }
            for r in rows
        ]

    def get_item(self, user_id: int, item_id: int) -> Optional[dict]:
        r = (
            self.db.execute(
                select(CartItem).where(
                    CartItem.user_id == user_id,
                    CartItem.item_id == item_id,
                )
            )
            .scalar_one_or_none()
        )
        if r is None:
            return None
        return {
            "item_id": r.item_id,
            "user_id": r.user_id,
            "product_id": r.product_id,
            "analysis_snapshot": r.analysis_snapshot,
        }

    def create_item(
        self,
        user_id: int,
        product_id: str,
        analysis_snapshot: Optional[Dict[str, Any]] = None,
    ) -> dict:
        obj = CartItem(
            user_id=user_id,
            product_id=product_id,
            analysis_snapshot=analysis_snapshot,
        )
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)

        return {
            "item_id": obj.item_id,
            "user_id": obj.user_id,
            "product_id": obj.product_id,
            "analysis_snapshot": obj.analysis_snapshot,
        }

    def delete_item(self, user_id: int, item_id: int) -> bool:
        result = self.db.execute(
            delete(CartItem).where(
                CartItem.user_id == user_id,
                CartItem.item_id == item_id,
            )
        )
        deleted = result.rowcount or 0
        if deleted == 0:
            return False
        self.db.commit()
        return True