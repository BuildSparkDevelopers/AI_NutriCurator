from __future__ import annotations

from typing import Any, Dict, Optional


class FakeUserRepository:
    def __init__(self, users: Dict[Any, Dict[str, Any]]):
        self.users = users

    def get_by_id(self, user_id: int) -> Optional[dict]:
        user = self.users.get(user_id)
        if user:
            return user
        return {"user_id": user_id, "email": f"user{user_id}@fake.local"}
