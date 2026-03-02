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

    diabetes_detail: Literal["type1", "type2", "pre_type1", "pre_type2", "na"] #"TYPE_1", "TYPE_2", "GESTATIONAL"
    hypertension_detail: Literal["prehypertension", "stage1", "stage2", "na"] #"STAGE_1", "STAGE_2"
    kidney_detail: Literal["CKD_3_5", "HD", "PD", "na"]
    allergy_list: List[str]
    allergy_detail: List[str]

    #guidelines: List[str]
    final_profile: dict

    # [chat-Agent가 채워줄 정보]
    any_exceed : bool
    exceeded_nutrients: List[str]

    any_allergen: bool          # 제품에 알러지 유발 물질이 포함되었는가?
    substitute: List[str]      # 추천 대체 식재료 목록

    allergy_safety_summary: str
    warning : bool
    threshold_checked: bool

    # [흐름 제어]
    next_step: str
    final_answer: str              # 사용자에게 보여줄 최종 답변

    # [서브 레코 에이전트 용 정보]
    candidates: List[dict]
    sub_recommendations: List[dict]