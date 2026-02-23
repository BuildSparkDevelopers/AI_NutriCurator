# domain/services/auth_service.py

from app.security import (
    validate_username,
    validate_password,
    hash_password,
    verify_password,
    create_access_token,
    decode_token,
    blacklist_token_jti,
    utc_now,
)
from app.settings import settings


class AuthService:
    def __init__(self, user_repo):
        self.user_repo = user_repo

    def signup(
        self,
        *,
        username: str,   # 지금은 username으로 받되, email로 취급
        password: str,
        is_tos_agreed: bool,
        is_privacy_agreed: bool,
        is_sensitive_agreed: bool,
    ) -> dict:
        validate_username(username)
        validate_password(password)

        if not is_tos_agreed:
            raise ValueError("TOS_NOT_AGREED")
        if not is_privacy_agreed:
            raise ValueError("PRIVACY_NOT_AGREED")

        email = username

        if self.user_repo.get_by_email(email) is not None:
            raise ValueError("EMAIL_ALREADY_EXISTS")

        now = utc_now()

        user = self.user_repo.create(
            email=email,
            password_hash=hash_password(password),
            created_at=now,
            updated_at=now,
            is_sensitive_agreed=is_sensitive_agreed,
            agreed_at=(now if is_sensitive_agreed else None),
            is_tos_agreed=is_tos_agreed,
            is_privacy_agreed=is_privacy_agreed,
        )

        token = create_access_token(
            subject=str(user["user_id"]),
            secret_key=settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
            expires_minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
        return {"access_token": token, "token_type": "bearer"}

    def login(self, *, username: str, password: str) -> dict:
        email = username
        user = self.user_repo.get_by_email(email)
        if user is None:
            raise ValueError("INVALID_CREDENTIALS")

        if not verify_password(password, user["password_hash"]):
            raise ValueError("INVALID_CREDENTIALS")

        token = create_access_token(
            subject=str(user["user_id"]),
            secret_key=settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
            expires_minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
        return {"access_token": token, "token_type": "bearer"}

    def logout(self, *, token: str) -> None:
        payload = decode_token(token, settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM)
        jti = payload.get("jti")
        if jti:
            blacklist_token_jti(jti)