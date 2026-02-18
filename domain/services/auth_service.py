 # 역할: 회원가입/로그인/로그아웃 유스케이스(업무 흐름)
 # - 정책 검증, 약관 동의, 중복 체크, 비번 해싱, 토큰 발급/폐기

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
        username: str,
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

        if self.user_repo.get_by_username(username) is not None:
            raise ValueError("USERNAME_ALREADY_EXISTS")

        now = utc_now()
        user = self.user_repo.create(
            username=username,
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
            expires_minutes=settings.JWT_EXPIRES_MINUTES,
        )
        return {"access_token": token, "token_type": "bearer"}

    def login(self, *, username: str, password: str) -> dict:
        user = self.user_repo.get_by_username(username)
        if user is None:
            raise ValueError("INVALID_CREDENTIALS")

        if not verify_password(password, user["password_hash"]):
            raise ValueError("INVALID_CREDENTIALS")

        token = create_access_token(
            subject=str(user["user_id"]),
            secret_key=settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
            expires_minutes=settings.JWT_EXPIRES_MINUTES,
        )
        return {"access_token": token, "token_type": "bearer"}

    def logout(self, *, token: str) -> None:
        payload = decode_token(token, settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM)
        jti = payload.get("jti")
        if jti:
            blacklist_token_jti(jti)
