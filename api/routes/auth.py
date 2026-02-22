 # 역할: 회원가입/로그인/로그아웃 HTTP 엔드포인트
 # - 요청/응답만 담당하고 실제 로직은 AuthService로 위임

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from api.schemas.auth import SignupRequest, LoginRequest, TokenResponse
from api.deps import get_auth_service, bearer_scheme
from domain.services.auth_service import AuthService

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

@router.post("/signup", response_model=TokenResponse)
def signup(payload: SignupRequest, service: AuthService = Depends(get_auth_service)):
    try:
        return service.signup(
            username=payload.username,
            password=payload.password,
            is_tos_agreed=payload.is_tos_agreed,
            is_privacy_agreed=payload.is_privacy_agreed,
            is_sensitive_agreed=payload.is_sensitive_agreed,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, service: AuthService = Depends(get_auth_service)):
    try:
        return service.login(username=payload.username, password=payload.password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/logout")
def logout(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    service: AuthService = Depends(get_auth_service),
):
    if credentials is None:
        raise HTTPException(status_code=401, detail="MISSING_TOKEN")
    if credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="INVALID_AUTH_SCHEME")

    try:
        service.logout(token=credentials.credentials)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"ok": True}
