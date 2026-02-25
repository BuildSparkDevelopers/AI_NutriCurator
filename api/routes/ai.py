from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Any, Dict

from api.deps import get_current_user_id, get_user_service, get_product_service
from ai.orchestrator.graph import compile_graph

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
        
        # 3. Overall State 구성
        # user_agent_node가 단일 기준으로 flag/final_profile을 계산하도록
        # 초기 state에는 raw profile만 전달한다.
        overall_state = {
            "user_id": str(user_id),
            "product_id": str(req.product_id),
            "name": product_detail.get("name", ""),
            "user_profile": health_profile,
            "product_data": product_detail,

            # 분석 결과 (초기값)
            "any_exceed": False,
            "any_allergen": False,
            "exceeded_nutrients": [],
            "next_step": "",
            "final_answer": ""
        }
        
        # 4. 분석용 상품 인덱스 주입 후 Orchestrator 실행
        products_db = product_service.get_products_index()
        app = compile_graph(products_db=products_db, final_profiles={})
        
        # 그래프 실행. 전체 노드를 순회하고 최종 상태(Dict)를 받습니다.
        final_state = app.invoke(overall_state)
        
        # 5. 결과 구성 (LangGraph 최종 state 기반)
        decision = "safe"  # 기본값
        reason_summary = final_state.get("final_answer", "")
        raw_alternatives = final_state.get("sub_recommendations", [])

        # alternatives 풍부화: product_id → name, image_url, reason(키워드)
        alternatives = []
        for alt in raw_alternatives:
            pid = alt.get("product_id")
            try:
                detail = product_service.get_product_detail(product_id=str(pid)) if pid else {}
            except (ValueError, Exception):
                detail = {}
            alternatives.append({
                "product_id": pid,
                "id": pid,
                "name": detail.get("name") or alt.get("name") or f"상품 {pid}",
                "image_url": detail.get("image_url"),
                "reason": alt.get("reason", ""),
            })
        
        any_exceed = final_state.get("any_exceed", False)
        any_allergen = final_state.get("any_allergen", False)
        
        # 정책에 따른 결과 해석 (프론트엔드 호환용)
        if not any_exceed and not any_allergen:
            decision = "safe"
            if not reason_summary:
                reason_summary = f"✅ {product_detail.get('name')}은(는) 건강 프로필상 안전한 상품입니다."
        elif any_exceed or any_allergen:
            decision = "warning"
            if not reason_summary:
                exceed_list = final_state.get("exceeded_nutrients", [])
                allergen_info = " 알러지 유발 성분이 포함되어 있습니다." if any_allergen else ""
                reason_summary = f"⚠️ 이 상품은 {', '.join(exceed_list) if exceed_list else '건강 기준'}에 맞지 않습니다.{allergen_info}"
        else:
            decision = "caution"
            if not reason_summary:
                reason_summary = f"⚡ {product_detail.get('name')}을(를) 섭취할 때 주의가 필요합니다."
        
        return {
            "status": "ok",
            "decision": decision,
            "reason_summary": reason_summary,
            "alternatives": alternatives,
            "product_name": product_detail.get("name", ""),
            "next_step": final_state.get("next_step", "end"),
            "full_state_debug": final_state # 프론트에서 전체 상태를 확인해볼 수 있게 임시 추가
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"분석 중 오류가 발생했습니다: {str(e)}"
        )
