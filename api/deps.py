# 역할:
# 1) DB(store) -> repo -> service를 조립해서 Depends로 제공
# 2) Authorization Bearer 토큰에서 user_id(sub) 뽑기
# 3) 로그아웃 토큰(jti) 블랙리스트 체크
# # 중요:
# # - /docs Authorize에는 토큰만 넣으면 됨 (HTTPBearer가 Bearer 자동)

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from infra.db.session import get_db
from infra.db.repositories.user_repo import UserRepository
from infra.db.repositories.health_repo import HealthProfileRepository
from infra.db.repositories.product_repo import ProductRepository
from domain.services.product_service import ProductService

from domain.services.auth_service import AuthService
from domain.services.user_service import UserService

from app.security import decode_token, is_token_blacklisted
from app.settings import settings

bearer_scheme = HTTPBearer(auto_error=False)

def get_repos(db=Depends(get_db)):
    return UserRepository(db), HealthProfileRepository(db)

def get_auth_service(repos=Depends(get_repos)) -> AuthService:
    user_repo, _ = repos
    return AuthService(user_repo)

def get_user_service(repos=Depends(get_repos)) -> UserService:
    user_repo, health_repo = repos
    return UserService(user_repo, health_repo)

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

    return int(sub)

def get_product_repo(db=Depends(get_db)) -> ProductRepository:
    # # 역할: ProductRepository 주입
    return ProductRepository(db)

def get_product_service(repo: ProductRepository = Depends(get_product_repo)) -> ProductService:
    # # 역할: ProductService 주입
    return ProductService(repo)