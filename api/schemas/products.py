# 역할: 프론트/Swagger와 약속하는 데이터 모양 (응답 스키마)

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class ProductSummary(BaseModel):
    product_id: str
    name: str
    category: Optional[str] = None
    brand: Optional[str] = None
    price: Optional[int] = None
    image_url: Optional[str] = None

class ProductListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: List[ProductSummary]

class ProductDetailResponse(BaseModel):
    product_id: str
    name: str
    category: Optional[str] = None
    brand: Optional[str] = None
    price: Optional[int] = None
    image_url: Optional[str] = None
    description: Optional[str] = None

    ingredients: List[str] = Field(default_factory=list)
    allergy: Optional[str] = None
    trace: Optional[str] = None

    calories: Optional[float] = None
    sodium: Optional[float] = None
    carbohydrate: Optional[float] = None
    sugar: Optional[float] = None
    fat: Optional[float] = None
    trans_fat: Optional[float] = None
    saturated_fat: Optional[float] = None
    cholesterol: Optional[float] = None
    protein: Optional[float] = None
    phosphorus: Optional[float] = None
    calcium: Optional[float] = None
    potassium: Optional[float] = None

    inferred_types: List[str] = Field(default_factory=list)

    # 혹시 이후 영양정보를 dict로 확장할 때 대비 (선택)
    nutrients: Dict[str, Any] = Field(default_factory=dict)

