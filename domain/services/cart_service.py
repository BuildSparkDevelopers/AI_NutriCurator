# 역할: 장바구니 유스케이스
# - 중복 담기 방지(같은 product_id면 기존 item 반환)
# - product_id 숫자 검증 + products 존재 검증

from typing import Optional, Dict, Any, List


class CartService:
    def __init__(self, cart_repo, product_repo):
        self.cart_repo = cart_repo
        self.product_repo = product_repo

    def add_item(
        self,
        *,
        user_id: int,
        product_id: str,
        analysis_snapshot: Optional[Dict[str, Any]] = None,
    ) -> dict:
        # 1) product_id 정규화 + 숫자 검증 ("0010" -> "10")
        try:
            product_id = str(int(str(product_id).strip()))
        except ValueError:
            raise ValueError("PRODUCT_ID_MUST_BE_DIGITS")

        # 2) products 존재 여부 검증
        if self.product_repo.get_by_id(product_id) is None:
            raise ValueError("PRODUCT_NOT_FOUND")

        # 3) 중복 담기 방지(같은 product_id면 기존 item 반환)
        items = self.cart_repo.list_items(user_id=user_id)
        for it in items:
            if str(it.get("product_id")) == product_id:
                return it

        # 4) 새로 담기
        return self.cart_repo.create_item(
            user_id=user_id,
            product_id=product_id,
            analysis_snapshot=analysis_snapshot,
        )

    def list_items(self, *, user_id: int) -> List[dict]:
        return self.cart_repo.list_items(user_id=user_id)

    def remove_item(self, *, user_id: int, item_id: int) -> None:
        ok = self.cart_repo.delete_item(user_id=user_id, item_id=item_id)
        if not ok:
            raise ValueError("CART_ITEM_NOT_FOUND")