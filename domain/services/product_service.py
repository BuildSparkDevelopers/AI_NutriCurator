
# 역할: 상품 목록/상세 조회 유스케이스
# - repo에서 raw data 가져오고, API에서 쓰기 좋은 형태로 정리
#  - 목록 필터(카테고리/검색어/페이징) 같은 정책은 여기서 담당

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
        # # 역할: 메인/카테고리 페이지용 상품 리스트 제공
        # # - category: 카테고리 필터
        # # - q: 검색어(상품명에 포함)
        # # - limit/offset: 페이징

        # MVP: 비어있으면 테스트 데이터 자동 주입
        self.product_repo.seed_if_empty()

        items: List[dict] = self.product_repo.list_all()

        if category:
            items = [x for x in items if (x.get("category") == category)]

        if q:
            q_lower = q.strip().lower()
            items = [x for x in items if (q_lower in (x.get("name", "").lower()))]

        total = len(items)

        # 페이징 안전장치
        if offset < 0:
            offset = 0
        if limit <= 0:
            limit = 20

        paged = items[offset : offset + limit]

        return {"total": total, "items": paged, "limit": limit, "offset": offset}

    def get_product_detail(self, *, product_id: str) -> dict:
        # # 역할: 상세 페이지용 상품 단건 조회
        self.product_repo.seed_if_empty()

        product = self.product_repo.get_by_id(product_id)
        if product is None:
            raise ValueError("PRODUCT_NOT_FOUND")
        return product
