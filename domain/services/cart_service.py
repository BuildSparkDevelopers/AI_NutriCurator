
# 역할: 장바구니 유스케이스
# - 중복 담기 방지(같은 product_id면 기존 item 반환)


from typing import Optional, Dict, Any, List

class CartService:
    def __init__(self, cart_repo):
        self.cart_repo = cart_repo

    def add_item(
        self,
        *,
        user_id: str,
        product_id: str,
        analysis_snapshot: Optional[Dict[str, Any]] = None,
    ) -> dict:
        # # 역할: 장바구니 담기
        # # 정책: 같은 상품(product_id)은 중복 담기 방지 → 기존 item 그대로 반환 (idempotent)
        items = self.cart_repo.list_items(user_id)
        for it in items:
            if it.get("product_id") == product_id:
                # 이미 담겨있으면 그대로 반환
                return it

        return self.cart_repo.create_item(user_id, product_id, analysis_snapshot)

    def list_items(self, *, user_id: str) -> List[dict]:  
        # 역할: 장바구니 목록 조회
        return self.cart_repo.list_items(user_id)

    def remove_item(self, *, user_id: str, item_id: int) -> None:
        # 역할: 장바구니 삭제
        ok = self.cart_repo.delete_item(user_id, item_id)
        if not ok:
            raise ValueError("CART_ITEM_NOT_FOUND")