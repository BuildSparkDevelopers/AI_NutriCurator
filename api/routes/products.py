# 역할: 상품 목록/상세 조회 API (HTTP 처리만)
# - 실제 로직은 service에 위임

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from api.schemas.products import ProductListResponse, ProductDetailResponse
from api.deps import get_product_service
from domain.services.product_service import ProductService

router = APIRouter(prefix="/api/v1/products", tags=["products"])

@router.get("", response_model=ProductListResponse)
def list_products(
    category: Optional[str] = Query(default=None),
    q: Optional[str] = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    service: ProductService = Depends(get_product_service),
):
    # # 역할: 메인/카테고리 상품 리스트 (필터 포함)
    return service.list_products(category=category, q=q, limit=limit, offset=offset)

@router.get("/{product_id}", response_model=ProductDetailResponse)
def get_product_detail(
    product_id: str,
    service: ProductService = Depends(get_product_service),
):
    # # 역할: 상세 페이지 상품 조회 (영양성분/설명 포함)
    try:
        return service.get_product_detail(product_id=product_id)
    except ValueError as e:
        if str(e) == "PRODUCT_NOT_FOUND":
            raise HTTPException(status_code=404, detail="PRODUCT_NOT_FOUND")
        raise HTTPException(status_code=400, detail=str(e))
