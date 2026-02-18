# DB 없이 MVP를 위한 In-Memory 저장소

from dataclasses import dataclass, field
from typing import Dict

@dataclass
class InMemoryStore:
    users: Dict[int, dict] = field(default_factory=dict)
    username_to_user_id: Dict[str, int] = field(default_factory=dict)
    health_profiles: Dict[int, dict] = field(default_factory=dict)
    next_user_id: int = 1

    # products
    products: Dict[str, dict] = field(default_factory=dict)

    
    next_user_id: int = 1

STORE = InMemoryStore()
