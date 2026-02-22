# 역할: 내 프로필 저장/조회 HTTP 엔드포인트
# - 인증 필요: get_current_user_id로 user_id 확보 후 service 호출

from fastapi import APIRouter, Depends, HTTPException

from api.schemas.users import HealthProfileUpsertRequest, HealthProfileResponse
from api.deps import get_user_service, get_current_user_id
from domain.services.user_service import UserService

router = APIRouter(prefix="/api/v1/users", tags=["users"])

@router.post("/me/profile", response_model=HealthProfileResponse)
def upsert_my_profile(
    payload: HealthProfileUpsertRequest,
    user_id: int = Depends(get_current_user_id),
    service: UserService = Depends(get_user_service),
):
    try:
        profile = service.upsert_my_profile(user_id=user_id, profile=payload.model_dump())
        return {"user_id": user_id, "profile": profile}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/me/profile", response_model=HealthProfileResponse)
def get_my_profile(
    user_id: int = Depends(get_current_user_id),
    service: UserService = Depends(get_user_service),
):
    try:
        profile = service.get_my_profile(user_id=user_id)
        return {"user_id": user_id, "profile": profile}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
