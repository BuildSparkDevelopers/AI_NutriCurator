# 유저 인증/보안 유틸 모음
# - username/password 정책 검증
# - 비밀번호 해시/검증 (bcrypt)
# - JWT 토큰 생성/검증 (python-jose)
# - 로그아웃 토큰 폐기(블랙리스트 jti)

import re
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from jose import jwt, JWTError
from passlib.context import CryptContext

from app.settings import settings


# 0) 시간 유틸

def utc_now() -> datetime:
    # timezone-aware UTC now
    return datetime.now(timezone.utc)


# 1) 비밀번호 해시

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)

# 2) username/password 정책 검증

_USERNAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]{3,19}$")
# 첫 글자 영문, 이후 영문/숫자/언더스코어, 총 4~20자 (settings 기준과 일치)

def validate_username(username: str) -> None:
    # 역할: username 규칙 위반 시 ValueError 발생
    if not (settings.USERNAME_MIN_LEN <= len(username) <= settings.USERNAME_MAX_LEN):
        raise ValueError("USERNAME_LENGTH_INVALID")
    if not _USERNAME_RE.match(username):
        raise ValueError("USERNAME_FORMAT_INVALID")

def validate_password(password: str) -> None:
    # 역할: password 규칙 위반 시 ValueError 발생
    if " " in password:
        raise ValueError("PASSWORD_NO_SPACES")

    if not (settings.PASSWORD_MIN_LEN <= len(password) <= settings.PASSWORD_MAX_LEN):
        raise ValueError("PASSWORD_LENGTH_INVALID")

    # 최소 조건: 대문자/소문자/숫자/특수문자 각각 1개 이상
    if not re.search(r"[A-Z]", password):
        raise ValueError("PASSWORD_NEEDS_UPPERCASE")
    if not re.search(r"[a-z]", password):
        raise ValueError("PASSWORD_NEEDS_LOWERCASE")
    if not re.search(r"[0-9]", password):
        raise ValueError("PASSWORD_NEEDS_DIGIT")
    if not re.search(r"[^A-Za-z0-9]", password):
        raise ValueError("PASSWORD_NEEDS_SPECIAL")


# 3) JWT 생성/검증

def create_access_token(
    *,
    subject: str,
    secret_key: str,
    algorithm: str,
    expires_minutes: int,
) -> str:
    # 역할: (sub=user_id) + (jti=토큰 식별자) 포함한 access token 발급
    now = utc_now()
    exp = now + timedelta(minutes=expires_minutes)

    payload = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
        "jti": str(uuid.uuid4()),
        "type": "access",
    }
    return jwt.encode(payload, secret_key, algorithm=algorithm)

def decode_token(token: str, secret_key: str, algorithm: str) -> Dict[str, Any]:
    # 역할: 토큰 검증(서명/만료) 실패 시 ValueError
    
    # Mock 토큰 처리 (개발 전용)
    # 형식: "header.payload.mock_signature"
    if token.endswith(".mock_signature"):
        try:
            parts = token.split(".")
            if len(parts) == 3:
                import json
                import base64
                payload_b64 = parts[1]
                # Base64 padding 추가
                padding = 4 - len(payload_b64) % 4
                if padding != 4:
                    payload_b64 += '=' * padding
                payload_json = base64.urlsafe_b64decode(payload_b64).decode('utf-8')
                payload = json.loads(payload_json)
                return payload
        except Exception:
            raise ValueError("INVALID_TOKEN")
    
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        return payload
    except JWTError:
        raise ValueError("INVALID_TOKEN")


# 4) 로그아웃용 블랙리스트(jti)

# MVP: 메모리 set
# - 서버 재시작하면 초기화됨(=개발/데모용)
_TOKEN_BLACKLIST = set()

def blacklist_token_jti(jti: str) -> None:
    # 역할: 로그아웃 시 현재 토큰의 jti를 저장(폐기)
    _TOKEN_BLACKLIST.add(jti)

def is_token_blacklisted(jti: str) -> bool:
    # 역할: 토큰이 폐기되었는지 확인
    return jti in _TOKEN_BLACKLIST
