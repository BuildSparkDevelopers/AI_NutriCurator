# DB 없이 MVP를 위한 In-Memory 저장소

from dataclasses import dataclass, field
from typing import Dict,Any,List

@dataclass
class InMemoryStore:
    users: Dict[int, dict] = field(default_factory=dict)
    username_to_user_id: Dict[str, int] = field(default_factory=dict)
    health_profiles: Dict[int, dict] = field(default_factory=dict)
    next_user_id: int = 1

    # products
    products: Dict[str, dict] = field(default_factory=dict)

    
    next_user_id: int = 1

    # cart_items (user_id별로 장바구니 항목 list 보관)
    # 예) cart_items["user123"] = [{"item_id": 1, "product_id": "201905...", "analysis_snapshot": {...}}, ...]
    cart_items: Dict[str, List[dict]] = field(default_factory=dict)
    next_cart_item_id: int = 1


STORE = InMemoryStore()   

