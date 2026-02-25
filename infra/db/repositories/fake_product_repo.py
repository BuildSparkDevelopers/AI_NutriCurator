from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple


class FakeProductRepository:
    def __init__(self, products: Dict[str, Dict[str, Any]]):
        self.products = products

    def exists(self, product_id: str | int) -> bool:
        pid = str(product_id)
        return any(str(p.get("product_id")) == pid for p in self.products.values())

    def get_by_id(self, product_id: str) -> Optional[dict]:
        pid = str(product_id)
        for _, product in self.products.items():
            if str(product.get("product_id")) == pid:
                return {
                    "product_id": str(product.get("product_id")),
                    "name": product.get("name"),
                    "category": product.get("category"),
                    "brand": product.get("brand"),
                    "price": None,
                    "image_url": product.get("image_url"),
                    "description": None,
                    "ingredients": product.get("ingredients", []),
                    "allergy": product.get("allergy"),
                    "trace": product.get("trace"),
                    "calories": product.get("calories"),
                    "sodium": product.get("sodium"),
                    "carbohydrate": product.get("carbohydrate"),
                    "sugar": product.get("sugar"),
                    "fat": product.get("fat"),
                    "trans_fat": product.get("trans_fat"),
                    "saturated_fat": product.get("saturated_fat"),
                    "cholesterol": product.get("cholesterol"),
                    "protein": product.get("protein"),
                    "phosphorus": product.get("phosphorus"),
                    "calcium": product.get("calcium"),
                    "potassium": product.get("potassium"),
                    "inferred_types": product.get("inferred_types", []),
                    "nutrients": {},
                }
        return None

    def list_products(
        self,
        *,
        category: Optional[str] = None,
        q: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> Tuple[List[dict], int]:
        items = []
        q_l = (q or "").strip().lower()
        cat_l = (category or "").strip().lower()
        for _, product in self.products.items():
            if cat_l and cat_l not in str(product.get("category", "")).lower():
                continue
            name = str(product.get("name", ""))
            brand = str(product.get("brand", ""))
            if q_l and q_l not in name.lower() and q_l not in brand.lower():
                continue
            items.append(
                {
                    "product_id": str(product.get("product_id")),
                    "name": name,
                    "category": product.get("category"),
                    "brand": brand,
                    "price": None,
                    "image_url": product.get("image_url"),
                }
            )

        total = len(items)
        sliced = items[offset : offset + limit]
        return sliced, total

    def get_products_index(self) -> Dict[str, Dict[str, Any]]:
        """
        분석용 상품 맵을 product_id 키 기준으로 반환.
        """
        indexed: Dict[str, Dict[str, Any]] = {}
        for product in self.products.values():
            pid = str(product.get("product_id") or "").strip()
            if not pid:
                continue
            indexed[pid] = dict(product)
        return indexed
