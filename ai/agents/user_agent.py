from typing import List, Dict, Any, TypedDict
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.runnables import RunnableConfig



# 1. LLM 구조화 출력을 위한 Pydantic 모델
class HealthAnalysis(BaseModel):
    """질병 정보에 기반한 식이 가이드 및 주의 성분"""
    guidelines: List[str] = Field(
        ...,
        description="환자의 질병 정보를 바탕으로 한 구체적인 식단 가이드라인 3~5가지"
    )
    target_ingredients: List[str] = Field(
        ...,
        description="해당 질병 보유자가 피해야 하거나 주의해야 할 핵심 성분명 리스트 (예: 나트륨, 당류, 포화지방)"
    )

# 2. User Agent 클래스 (ProfileRetrieval)
class ProfileRetrieval:
    def __init__(self, model):
        """
        Args:
            model: 구조화된 출력을 지원하는 LLM 객체 (예: ChatOpenAI)
        """
        self.llm = model
        # LLM이 Pydantic 모델에 맞춰 답하도록 설정
        self.analysis_chain = self.llm.with_structured_output(HealthAnalysis)

    def _fetch_profile_from_backend(self, user_id: str) -> Dict[str, Any]:
        """
        [Mock API] user_id를 'Key'로 사용하여 백엔드 DB에서 유저 정보를 조회함.
        실제로는 requests.get(f"api/user/{user_id}") 형태가 됨.
        """
        print(f"📡 [User-Agent] 백엔드 조회 중... (Target ID: {user_id})")

        # 임시 DB (Mock Data)
        mock_db = {
            "user_001": {
                "name": "김철수",
                "diabetes": 1,        # 당뇨 있음
                "hypertension": 1,    # 고혈압 있음
                "kidneydisease": 0,
                "allergy": 0
            },
            "user_002": {
                "name": "이영희",
                "diabetes": 0,
                "hypertension": 0,
                "kidneydisease": 1,   # 신장질환 있음
                "allergy": 1          # 알러지 있음
            }
        }

        # DB에 없으면 기본값 반환
        return mock_db.get(user_id, {
            "name": "Unknown", "diabetes": 0, "hypertension": 0, "kidneydisease": 0, "allergy": 0
        })

    def run(self, state: OverallState, config: RunnableConfig = None) -> Dict[str, Any]:
        """LangGraph 노드 실행 함수"""

        # 1. State에서 user_id 꺼내기 (이미 있는 정보 활용)
        current_user_id = state.get("user_id")

        # 2. 백엔드 API를 통해 상세 프로필(질병 유무) 가져오기
        user_profile = self._fetch_profile_from_backend(current_user_id)

        # 3. LLM에게 분석 요청 (0/1 데이터를 텍스트 가이드로 변환)
        #    프롬프트에 질병 정보를 요약해서 전달
        health_summary = (
            f"당뇨: {'있음' if user_profile['diabetes'] else '없음'}, "
            f"고혈압: {'있음' if user_profile['hypertension'] else '없음'}, "
            f"신장질환: {'있음' if user_profile['kidneydisease'] else '없음'}, "
            f"알러지: {'있음' if user_profile['allergy'] else '없음'}"
        )

        system_msg = "당신은 임상 영양사입니다. 환자의 질병 정보를 바탕으로 식단 가이드와 주의 성분을 추출하세요."

        # LLM 호출 (구조화된 출력 반환)
        analysis_result: HealthAnalysis = self.analysis_chain.invoke([
            SystemMessage(content=system_msg),
            HumanMessage(content=f"환자 정보: {health_summary}")
        ])

        print(f"✅ [User-Agent] 분석 완료: {analysis_result.target_ingredients}")

        # 4. State 업데이트 (스키마에 맞춰서 반환)
        return {
            # (1) 백엔드에서 가져온 Raw Data
            "name": user_profile["name"],
            "diabetes": user_profile["diabetes_flag"],
            "hypertension": user_profile["hypertension_flag"],
            "kidneydisease": user_profile["kidneydisease_flag"],
            "allergy": user_profile["allergy_flag"],

            "diabetes_type": user_profile["diabetes_detail"],
            "hypertension_type": user_profile["hypertension_detail"],
            "kidneydisease_type": user_profile["kidneydisease_detail"],
            "allergy_list": user_profile["allergy_list"],

            "final_profile": user_profile, # 임계값

            # (4) 흐름 제어 (오케스트레이터에게 턴을 넘김)
            "next_step": "orch_agent"
        }

# --- 사용 예시 ---

# 1. LLM 정의 (앞서 만든 router_llm과 같은 모델 사용 가능)
# from langchain_openai import ChatOpenAI
# retrieval_llm = ChatOpenAI(model="gpt-4o", temperature=0)

# 2. 클래스 인스턴스 생성
useragent = ProfileRetrieval(retrieval_llm)

# 3. LangGraph에 노드 추가 시
# workflow.add_node("user_agent", useragent.run)
