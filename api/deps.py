# 역할:
# 1) DB(store) -> repo -> service를 조립해서 Depends로 제공
# 2) Authorization Bearer 토큰에서 user_id(sub) 뽑기
# 3) 로그아웃 토큰(jti) 블랙리스트 체크
# # 중요:
# # - /docs Authorize에는 토큰만 넣으면 됨 (HTTPBearer가 Bearer 자동)

from contextlib import contextmanager

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from infra.db.fake_data import load_fake_db

from infra.db.repositories.fake_user_repo import FakeUserRepository
from infra.db.repositories.fake_health_repo import FakeHealthProfileRepository
from infra.db.repositories.fake_product_repo import FakeProductRepository

from domain.services.auth_service import AuthService
from domain.services.user_service import UserService
from domain.services.product_service import ProductService
from domain.services.cart_service import CartService

from app.security import decode_token, is_token_blacklisted
from app.settings import settings

bearer_scheme = HTTPBearer(auto_error=False)


def _is_fake_mode() -> bool:
    return str(settings.AI_DATA_SOURCE).strip().lower() == "fake"


def get_db():
    from infra.db.session import get_db as _get_db

    yield from _get_db()


@contextmanager
def _session_scope():
    from infra.db.session import SessionLocal

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_repos(db=Depends(get_db)):
    from infra.db.repositories.user_repo import UserRepository
    from infra.db.repositories.health_repo import HealthProfileRepository

    return UserRepository(db), HealthProfileRepository(db)

def get_auth_service(repos=Depends(get_repos)) -> AuthService:
    user_repo, _ = repos
    return AuthService(user_repo)

def get_user_service():
    if _is_fake_mode():
        fake_db = load_fake_db()
        user_repo = FakeUserRepository(fake_db.get("users", {}))
        health_repo = FakeHealthProfileRepository(fake_db.get("users", {}))
        yield UserService(user_repo, health_repo)
        return

    from infra.db.repositories.user_repo import UserRepository
    from infra.db.repositories.health_repo import HealthProfileRepository

    with _session_scope() as db:
        user_repo = UserRepository(db)
        health_repo = HealthProfileRepository(db)
        yield UserService(user_repo, health_repo)

def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> int:
    if credentials is None:
        raise HTTPException(status_code=401, detail="MISSING_TOKEN")

    if credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="INVALID_AUTH_SCHEME")

    token = credentials.credentials

    try:
        payload = decode_token(token, settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM)
    except ValueError:
        raise HTTPException(status_code=401, detail="INVALID_TOKEN")

    jti = payload.get("jti")
    if jti and is_token_blacklisted(jti):
        raise HTTPException(status_code=401, detail="TOKEN_REVOKED")

    sub = payload.get("sub")
    if not sub:
        raise HTTPException(status_code=401, detail="INVALID_TOKEN")
    try:
        user_id = int(sub)
    except (TypeError, ValueError):
        raise HTTPException(status_code=401, detail="INVALID_TOKEN")

    if _is_fake_mode():
        fake_db = load_fake_db()
        users = fake_db.get("users", {})
        exists = False
        for value in users.values():
            try:
                if int(value.get("user_id", -1)) == user_id:
                    exists = True
                    break
            except (TypeError, ValueError):
                continue
        if not exists:
            raise HTTPException(status_code=401, detail="실제 사용자로 존재하지 않으면 회원가입이 필요합니다")
        return user_id

    from infra.db.repositories.user_repo import UserRepository

    with _session_scope() as db:
        user_repo = UserRepository(db)
        if user_repo.get_by_id(user_id) is None:
            raise HTTPException(status_code=401, detail="실제 사용자로 존재하지 않으면 회원가입이 필요합니다")
    return user_id

def get_product_repo():
    if _is_fake_mode():
        fake_db = load_fake_db()
        yield FakeProductRepository(fake_db.get("products", {}))
        return

    from infra.db.repositories.product_repo import ProductRepository

    with _session_scope() as db:
        yield ProductRepository(db)

def get_product_service(repo=Depends(get_product_repo)) -> ProductService:
    return ProductService(repo)

def get_cart_repo():
    from infra.db.repositories.cart_repo import CartRepository

    with _session_scope() as db:
        yield CartRepository(db)

def get_cart_service(
    cart_repo=Depends(get_cart_repo),
    product_repo=Depends(get_product_repo),
) -> CartService:
    return CartService(cart_repo, product_repo)