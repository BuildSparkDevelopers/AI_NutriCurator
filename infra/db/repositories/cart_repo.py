
#역할: cart 저장소 접근만 담당 (CRUD/조회)
# - 비즈니스 규칙(중복 처리, 응답 모양)은 service에서 담당

from typing import List, Optional, Dict, Any
from infra.db.store import InMemoryStore

class CartRepository:
    def __init__(self, db: InMemoryStore):
        self.db = db

    def list_items(self, user_id: str) -> List[dict]:
        return self.db.cart_items.get(user_id, [])

    def get_item(self, user_id: str, item_id: int) -> Optional[dict]:
        items = self.db.cart_items.get(user_id, [])
        for it in items:
            if it.get("item_id") == item_id:
                return it
        return None

    def create_item(self, user_id: str, product_id: str, analysis_snapshot: Optional[Dict[str, Any]] = None) -> dict:
        if user_id not in self.db.cart_items:
            self.db.cart_items[user_id] = []

        item = {
            "item_id": self.db.next_cart_item_id,
            "product_id": product_id,
            "analysis_snapshot": analysis_snapshot,
        }
        self.db.next_cart_item_id += 1

        self.db.cart_items[user_id].append(item)
        return item

    def delete_item(self, user_id: str, item_id: int) -> bool:
        items = self.db.cart_items.get(user_id, [])
        before = len(items)
        items = [it for it in items if it.get("item_id") != item_id]
        self.db.cart_items[user_id] = items
        return len(items) != before