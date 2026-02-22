# 역할: users CRUD만 담당 (정책/업무 규칙은 service에서)

from typing import Optional
from infra.db.store import InMemoryStore

class UserRepository:
    def __init__(self, db: InMemoryStore):
        self.db = db

    def get_by_username(self, username: str) -> Optional[dict]:
        user_id = self.db.username_to_user_id.get(username)
        if user_id is None:
            return None
        return self.db.users.get(user_id)

    def get_by_id(self, user_id: int) -> Optional[dict]:
        return self.db.users.get(user_id)

    def create(
        self,
        *,
        username: str,
        password_hash: str,
        created_at,
        updated_at,
        is_sensitive_agreed: bool,
        agreed_at,
        is_tos_agreed: bool,
        is_privacy_agreed: bool,
    ) -> dict:
        if username in self.db.username_to_user_id:
            raise ValueError("USERNAME_ALREADY_EXISTS")

        user_id = self.db.next_user_id
        self.db.next_user_id += 1

        user = {
            "user_id": user_id,
            "username": username,
            "password_hash": password_hash,
            "created_at": created_at,
            "updated_at": updated_at,
            "is_sensitive_agreed": is_sensitive_agreed,
            "agreed_at": agreed_at,
            "is_tos_agreed": is_tos_agreed,
            "is_privacy_agreed": is_privacy_agreed,
        }

        self.db.users[user_id] = user
        self.db.username_to_user_id[username] = user_id
        return user
