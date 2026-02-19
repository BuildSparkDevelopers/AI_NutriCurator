# 역할: 장바구니 API (HTTP 처리만)
# - 실제 로직은 service로 위임
# - 인증은 api/deps.py의 get_current_user_id 사용 (Bearer Token)

from fastapi import APIRouter, Depends, HTTPException, status

from api.schemas.cart import CartAddRequest, CartItemResponse, CartListResponse
from api.deps import get_cart_service, get_current_user_id
from domain.services.cart_service import CartService

router = APIRouter(prefix="/api/v1/cart", tags=["cart"])


@router.post("", response_model=CartItemResponse, status_code=status.HTTP_201_CREATED)
def add_to_cart(
    payload: CartAddRequest,
    user_id: int = Depends(get_current_user_id),
    service: CartService = Depends(get_cart_service),
):
    item = service.add_item(
        user_id=user_id,
        product_id=payload.product_id,
        analysis_snapshot=payload.analysis_snapshot,
    )
    return item


@router.get("", response_model=CartListResponse)
def list_cart(
    user_id: int = Depends(get_current_user_id),
    service: CartService = Depends(get_cart_service),
):
    items = service.list_items(user_id=user_id)
    return {"items": items}


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cart_item(
    item_id: int,
    user_id: int = Depends(get_current_user_id),
    service: CartService = Depends(get_cart_service),
):
    try:
        service.remove_item(user_id=user_id, item_id=item_id)
    except ValueError as e:
        if str(e) == "CART_ITEM_NOT_FOUND":
            raise HTTPException(status_code=404, detail="CART_ITEM_NOT_FOUND")
        raise HTTPException(status_code=400, detail=str(e))
    return None

