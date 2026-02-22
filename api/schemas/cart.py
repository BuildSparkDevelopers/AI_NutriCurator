#역할: 요청/응답 스키마 (Swagger 계약)

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class CartAddRequest(BaseModel):
    product_id: str = Field(..., min_length=1)
    analysis_snapshot: Optional[Dict[str, Any]] = None  # 없어도 됨(MVP)

class CartItemResponse(BaseModel):
    item_id: int
    product_id: str
    analysis_snapshot: Optional[Dict[str, Any]] = None

class CartListResponse(BaseModel):
    items: List[CartItemResponse] = Field(default_factory=list)