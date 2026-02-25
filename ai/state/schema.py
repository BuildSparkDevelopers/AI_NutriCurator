from typing import List, TypedDict, Literal
from enum import Enum

# 1. 중복적용이 가능한 질병 정보
class DiseaseInfo(TypedDict):
    group: str           # 4개 군 이름 (예: 'Allergy', 'Diabetes', 'Hypertension', 'Kidney disorder' 등)
    step: int            # 세부 단계 (예: 1, 2, 3)
    description: str     # 해당 단계에 대한 간략한 설명 (선택 사항)

# 2. 메인 클래스 (State)
class overallState(TypedDict):
    user_id: str
    product_id: str
    name: str
    user_profile: dict
    product_data: dict

    # [User-Agent가 채워줄 정보]
    diabetes_flag: int
    hypertension_flag: int
    kidneydisease_flag: int
    allergy_flag: int

    diabetes_detail: Literal["DIABETES"] | None #"TYPE_1", "TYPE_2", "GESTATIONAL"
    hypertension_detail: Literal["HYPERTENSION"] | None #"STAGE_1", "STAGE_2"
    kidney_detail: Literal["CKD_3_5", "HD", "PD"] | None
    allergy_list: List[str]

    #guidelines: List[str]
    final_profile: dict

    # [chat-Agent가 채워줄 정보]
    any_exceed : bool
    exceeded_nutrients: List[str]

    any_allergen: bool          # 제품에 알러지 유발 물질이 포함되었는가?
    substitute: List[str]      # 추천 대체 식재료 목록

    allergy_safety_summary: str
    warniing : bool
    threshold_checked: bool

    # [흐름 제어]
    next_step: str
    final_answer: str              # 사용자에게 보여줄 최종 답변

    # [서브 레코 에이전트 용 정보]
    candidates: List[dict]
    sub_recommendations: List[dict]


class KFDAAllergen(str, Enum):
    """식약처 고시 알레르기 유발물질 22종"""
    EGG = "난류(가금류)"
    MILK = "우유"
    BUCKWHEAT = "메밀"
    PEANUT = "땅콩"
    SOYBEAN = "대두"
    WHEAT = "밀"
    MACKEREL = "고등어"
    CRAB = "게"
    SHRIMP = "새우"
    PORK = "돼지고기"
    PEACH = "복숭아"
    TOMATO = "토마토"
    SULFITE = "아황산류"
    WALNUT = "호두"
    CHICKEN = "닭고기"
    BEEF = "쇠고기"
    SQUID = "오징어"
    SHELLFISH = "조개류(굴, 전복, 홍합 포함)"
    PINE_NUT = "잣"
    # ... (나머지 포함 총 22종)
