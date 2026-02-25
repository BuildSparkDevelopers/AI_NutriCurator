
from __future__ import annotations

from typing import Optional, List, Dict, Any


class ProductService:
    def __init__(self, product_repo):
        self.product_repo = product_repo

    def list_products(
        self,
        *,
        category: Optional[str] = None,
        q: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> Dict[str, Any]:
        # 페이징 안전장치 (기존 로직 유지)
        if offset < 0:
            offset = 0
        if limit <= 0:
            limit = 20

        items, total = self.product_repo.list_products(
            category=category,
            q=q,
            limit=limit,
            offset=offset,
        )

        return {"total": total, "items": items, "limit": limit, "offset": offset}

    def get_product_detail(self, *, product_id: str) -> dict:
        product = self.product_repo.get_by_id(product_id)
        if product is None:
            raise ValueError("PRODUCT_NOT_FOUND")
        return product

    def get_products_index(self) -> Dict[str, dict]:
        """
        분석 파이프라인(reco/sub-reco)에서 사용하는 상품 인덱스.
        key는 product_id 문자열로 통일한다.
        """
        if hasattr(self.product_repo, "get_products_index"):
            return self.product_repo.get_products_index()
        return {}