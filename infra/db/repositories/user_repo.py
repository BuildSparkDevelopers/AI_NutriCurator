# infra/db/repositories/user_repo.py
# 역할: users CRUD (DB Session 기반)
# - 정책/업무 규칙은 service(AuthService)에서
# infra/db/repositories/user_repo.py
# 역할: users CRUD (DB Session 기반)
# - 정책/업무 규칙은 service(AuthService)에서

from typing import Optional, Any, Dict
from sqlalchemy.orm import Session
from sqlalchemy import text


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def _row_to_dict(self, row) -> Optional[Dict[str, Any]]:
        return None if row is None else dict(row._mapping)

    def get_by_email(self, email: str) -> Optional[dict]:
        q = text("""
            SELECT user_id, email, password_hash, created_at, updated_at,
                   is_sensitive_agreed, agreed_at, is_tos_agreed, is_privacy_agreed
            FROM users
            WHERE email = :email
            LIMIT 1
        """)
        row = self.db.execute(q, {"email": email}).fetchone()
        return self._row_to_dict(row)

    # ✅ 기존 코드 호환 (username = email로 취급)
    def get_by_username(self, username: str) -> Optional[dict]:
        return self.get_by_email(username)

    def get_by_id(self, user_id: int) -> Optional[dict]:
        q = text("""
            SELECT user_id, email, password_hash, created_at, updated_at,
                   is_sensitive_agreed, agreed_at, is_tos_agreed, is_privacy_agreed
            FROM users
            WHERE user_id = :user_id
            LIMIT 1
        """)
        row = self.db.execute(q, {"user_id": user_id}).fetchone()
        return self._row_to_dict(row)

    def create(
        self,
        *,
        email: str,
        password_hash: str,
        created_at,
        updated_at,
        is_sensitive_agreed: bool,
        agreed_at,
        is_tos_agreed: bool,
        is_privacy_agreed: bool,
    ) -> dict:
        if self.get_by_email(email) is not None:
            raise ValueError("EMAIL_ALREADY_EXISTS")

        q = text("""
            INSERT INTO users (
                email, password_hash, created_at, updated_at,
                is_sensitive_agreed, agreed_at, is_tos_agreed, is_privacy_agreed
            )
            VALUES (
                :email, :password_hash, :created_at, :updated_at,
                :is_sensitive_agreed, :agreed_at, :is_tos_agreed, :is_privacy_agreed
            )
            RETURNING user_id, email, password_hash, created_at, updated_at,
                      is_sensitive_agreed, agreed_at, is_tos_agreed, is_privacy_agreed
        """)
        row = self.db.execute(q, {
            "email": email,
            "password_hash": password_hash,
            "created_at": created_at,
            "updated_at": updated_at,
            "is_sensitive_agreed": is_sensitive_agreed,
            "agreed_at": agreed_at,
            "is_tos_agreed": is_tos_agreed,
            "is_privacy_agreed": is_privacy_agreed,
        }).fetchone()

        self.db.commit()
        return self._row_to_dict(row)