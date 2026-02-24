from __future__ import annotations

from typing import List

from api.schemas.products import ProductSummary, ProductDetailResponse


def _split_ingredients(rawmtrl: str | None) -> List[str]:
    if not rawmtrl:
        return []
    # 원재료가 콤마/중점/슬래시 등 섞일 수 있어서 최대한 안전하게 분해
    txt = rawmtrl.replace("·", ",").replace("/", ",")
    items = [x.strip() for x in txt.split(",")]
    return [x for x in items if x]


def to_product_summary(p) -> ProductSummary:
    return ProductSummary(
        product_id=p.product_id,
        name=p.name,
        category=None,          # category_id만 있고 name 매핑은 아직이면 None
        brand=p.brand,
        price=None,             # price 컬럼이 DB에 없으면 None 유지
        image_url=p.image_url,
    )


def to_product_detail(p) -> ProductDetailResponse:
    # DB 컬럼명 → API 스키마명 매핑
    return ProductDetailResponse(
        product_id=p.product_id,
        name=p.name,
        category=None,
        brand=p.brand,
        price=None,
        image_url=p.image_url,
        description=None,

        ingredients=_split_ingredients(getattr(p, "rawmtrl", None)),
        allergy=getattr(p, "allergymtrl", None),
        trace=None,  # trace 컬럼 없으면 None

        calories=getattr(p, "kcal", None),
        sodium=getattr(p, "sodium_mg", None),
        carbohydrate=getattr(p, "carb_g", None),
        sugar=getattr(p, "sugar_g", None),
        fat=getattr(p, "fat_g", None),
        trans_fat=getattr(p, "trans_fat_g", None),
        saturated_fat=getattr(p, "sat_fat_g", None),
        cholesterol=getattr(p, "cholesterol_mg", None),
        protein=getattr(p, "protein_g", None),

        # DB에 아직 없으면 None
        phosphorus=None,
        calcium=None,
        potassium=None,

        inferred_types=[],
        nutrients={},  # 나중에 확장 대비
    )