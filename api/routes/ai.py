from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Any, Dict

from api.deps import get_current_user_id, get_user_service, get_product_service
from infra.db.repositories.generate_final_profile import generate_final_profile
from ai.orchestrator.policy import RouterLogic

router = APIRouter(prefix="/api/v1/ai", tags=["AI"])

class AnalyzeReq(BaseModel):
    product_id: int

@router.post("/analyze")
def analyze(
    req: AnalyzeReq, 
    user_id: int = Depends(get_current_user_id),
    user_service = Depends(get_user_service),
    product_service = Depends(get_product_service)
) -> Dict[str, Any]:
    """
    사용자의 건강 프로필을 기반으로 상품을 AI 분석하는 엔드포인트
    
    1. 사용자 건강 프로필 조회
    2. 상품 정보 조회
    3. Orchestrator 정책 실행
    4. 분석 결과 반환
    """
    
    try:
        # 1. 사용자 건강 프로필 조회
        health_profile = user_service.get_my_profile(user_id=user_id)
        
        if not health_profile:
            raise HTTPException(
                status_code=400, 
                detail="건강 프로필이 설정되지 않았습니다. 먼저 프로필을 완성해주세요."
            )
        
        # 2. 상품 정보 조회
        try:
            product_detail = product_service.get_product_detail(product_id=str(req.product_id))
        except ValueError as e:
            raise HTTPException(
                status_code=404, 
                detail="상품을 찾을 수 없습니다"
            )
        
        # 3. Health Profile을 Flag 형식으로 변환
        def convert_to_flag(value: str) -> int:
            """질환 상태를 flag로 변환 (N/A 또는 없음 -> 0, 그 외 -> 1)"""
            if not value or value.lower() in ["n/a", "none", ""]:
                return 0
            return 1
        
        diabetes_flag = convert_to_flag(health_profile.get("diabetes", "N/A"))
        hypertension_flag = convert_to_flag(health_profile.get("hypertension", "N/A"))
        kidneydisease_flag = convert_to_flag(health_profile.get("kidneydisease", "N/A"))
        allergy_flag = convert_to_flag(health_profile.get("allergy", ""))
        
        # 4. Overall State 구성
        overall_state = {
            "user_id": str(user_id),
            "product_id": str(req.product_id),
            "name": product_detail.get("name", ""),
            "user_profile": health_profile,
            "product_data": product_detail,
            
            # 건강 정보
            "diabetes_flag": diabetes_flag,
            "hypertension_flag": hypertension_flag,
            "kidneydisease_flag": kidneydisease_flag,
            "allergy_flag": allergy_flag,
            
            # 분석 결과 (초기값)
            "any_exceed": False,
            "any_allergen": False,
            "exceeded_nutrients": [],
            "next_step": "",
            "final_answer": ""
        }
        
        # 5. Orchestrator 정책 실행
        policy = RouterLogic()
        next_step = policy.run(overall_state)
        
        # 6. 결과 구성
        decision = "safe"  # 기본값
        reason_summary = ""
        alternatives = []
        
        # 정책에 따른 결과 해석
        if next_step == "end" and not overall_state.get("any_exceed") and not overall_state.get("any_allergen"):
            decision = "safe"
            reason_summary = f"✅ {product_detail.get('name')}은(는) 건강 프로필상 안전한 상품입니다."
        elif overall_state.get("any_exceed") or overall_state.get("any_allergen"):
            decision = "warning"
            exceed_list = overall_state.get("exceeded_nutrients", [])
            allergen_info = " 알러지 유발 성분이 포함되어 있습니다." if overall_state.get("any_allergen") else ""
            reason_summary = f"⚠️ 이 상품은 {', '.join(exceed_list) if exceed_list else '건강 기준'}에 맞지 않습니다.{allergen_info}"
        else:
            decision = "caution"
            reason_summary = f"⚡ {product_detail.get('name')}을(를) 섭취할 때 주의가 필요합니다."
        
        return {
            "status": "ok",
            "decision": decision,
            "reason_summary": reason_summary,
            "alternatives": alternatives,
            "product_name": product_detail.get("name", ""),
            "next_step": next_step
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"분석 중 오류가 발생했습니다: {str(e)}"
        )
