
from __future__ import annotations

from typing import Optional, List, Dict, Any, Tuple, Union

from sqlalchemy.orm import Session
from sqlalchemy import select, func, or_
from sqlalchemy import exists as sa_exists  

from domain.models.product import Product


class ProductRepository:
    """
    DB(Postgres) 기반
    - list_products: 검색/카테고리/페이징 + total
    - get_by_id: 상세 1건
    - 반환은 service에서 바로 스키마로 넣기 쉬운 dict 형태
    """

    def __init__(self, db: Session):
        self.db = db

    # -------------------------
    # 내부 유틸
    # -------------------------
    def _split_ingredients(self, rawmtrl: str | None) -> List[str]:
        if not rawmtrl:
            return []
        txt = rawmtrl.replace("·", ",").replace("/", ",")
        parts = [x.strip() for x in txt.split(",")]
        return [x for x in parts if x]

    def _parse_product_id(self, product_id: str) -> int:
        if not str(product_id).isdigit():
            raise ValueError("PRODUCT_ID_INVALID")
        return int(product_id)

    def _to_summary_dict(self, p: Product) -> Dict[str, Any]:
        return {
            "product_id": str(p.product_id),
            "name": p.name,
            "category": None,   # category join 전이라 None
            "brand": p.brand,
            "price": None,      # DB에 price 없음
            "image_url": p.image_url,
        }

    def _to_detail_dict(self, p: Product) -> Dict[str, Any]:
        return {
            "product_id": str(p.product_id),
            "name": p.name,
            "category": None,
            "brand": p.brand,
            "price": None,
            "image_url": p.image_url,
            "description": None,

            "ingredients": self._split_ingredients(getattr(p, "rawmtrl", None)),
            "allergy": getattr(p, "allergymtrl", None),
            "trace": None,

            "calories": getattr(p, "kcal", None),
            "sodium": getattr(p, "sodium_mg", None),
            "carbohydrate": getattr(p, "carb_g", None),
            "sugar": getattr(p, "sugar_g", None),
            "fat": getattr(p, "fat_g", None),
            "trans_fat": getattr(p, "trans_fat_g", None),
            "saturated_fat": getattr(p, "sat_fat_g", None),
            "cholesterol": getattr(p, "cholesterol_mg", None),
            "protein": getattr(p, "protein_g", None),

            # DB에 없으면 None
            "phosphorus": None,
            "calcium": None,
            "potassium": None,

            "inferred_types": [],
            "nutrients": {},
        }

    # -------------------------
    # ✅ 공개 메서드
    # -------------------------
    
    def exists(self, product_id: Union[str, int]) -> bool:
        pid = self._parse_product_id(product_id)
        stmt = select(sa_exists().where(Product.product_id == pid))
        return bool(self.db.execute(stmt).scalar())
    
    def get_by_id(self, product_id: str) -> Optional[dict]:
        pid = self._parse_product_id(product_id)
        stmt = select(Product).where(Product.product_id == pid)
        p = self.db.execute(stmt).scalars().first()
        if not p:
            return None
        return self._to_detail_dict(p)

    def list_products(
        self,
        *,
        category: Optional[str] = None,
        q: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> Tuple[List[dict], int]:
        stmt = select(Product)
        cnt_stmt = select(func.count()).select_from(Product)

        filters = []

        # category: 숫자면 category_id로 필터 (현재 DB 스펙 기준)
        if category and category.isdigit():
            filters.append(Product.category_id == int(category))

        # 검색어: name/brand
        if q:
            like = f"%{q.strip()}%"
            filters.append(or_(Product.name.ilike(like), Product.brand.ilike(like)))

        if filters:
            for f in filters:
                stmt = stmt.where(f)
                cnt_stmt = cnt_stmt.where(f)

        stmt = stmt.order_by(Product.product_id).limit(limit).offset(offset)

        rows = list(self.db.execute(stmt).scalars().all())
        total = int(self.db.execute(cnt_stmt).scalar() or 0)

        items = [self._to_summary_dict(p) for p in rows]
        return items, total
    
   