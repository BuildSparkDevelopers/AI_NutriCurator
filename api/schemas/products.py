# 역할: 프론트/Swagger와 약속하는 데이터 모양 (응답 스키마)

from __future__ import annotations

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator 


class ProductSummary(BaseModel):
    product_id: int  # DB는 int니까 int로 두는 게 안전 (문자열 필요하면 str로 바꿔도 됨)
    name: str
    category: Optional[str] = None
    brand: Optional[str] = None
    price: Optional[int] = None
    image_url: Optional[str] = None
    @field_validator("image_url")
    @classmethod
    def normalize_image_url(cls, v: Optional[str]):
        if not v:
            return v
        return v.replace("http://www.haccp.or.kr/", "https://www.haccp.or.kr/")
    


class ProductListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: List[ProductSummary]


class ProductDetailResponse(BaseModel):
    product_id: int
    name: str
    category: Optional[str] = None
    brand: Optional[str] = None
    price: Optional[int] = None
    image_url: Optional[str] = None
    description: Optional[str] = None
    @field_validator("image_url")
    @classmethod
    def normalize_image_url(cls, v: Optional[str]):
        if not v:
            return v
        return v.replace("http://www.haccp.or.kr/", "https://www.haccp.or.kr/")

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

    nutrients: Dict[str, Any] = Field(default_factory=dict)