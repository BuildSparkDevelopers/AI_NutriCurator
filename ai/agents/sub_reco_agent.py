# -*- coding: utf-8 -*-
"""
Sub-Recommendation Agent
- overallState의 질병 플래그를 기반으로 각 질병별 scoring 계산
- reco_agent에서 제공한 product_id들을 DB에서 조회하여 성분 비교
- 한글 DB 컬럼을 영어 인자로 매핑하여 scoring 함수 실행
- 점수가 높은 product_id를 추천 상태에 저장
"""

import json
from typing import TypedDict, List, Dict, Any, Optional
from dataclasses import dataclass, field

# ============================================================================
# 1. STATE 타입 정의
# ============================================================================

class Candidate(TypedDict):
    """reco_agent에서 전달받는 상품 후보"""
    product_id: int
    rank: int


class SubRecommendation(TypedDict):
    """sub-reco_agent에서 저장할 추천 결과"""
    product_id: int
    rank: int
    disease_type: str  # 'diabetes', 'hypertension', 'kidney_disease'
    score: float
    reason: str


# ============================================================================
# 2. 컬럼 매퍼 (한글 DB ↔ 영어 코드)
# ============================================================================

class ColumnMapper:
    """
    DB의 한글 컬럼명과 Python 영어 변수명 간의 매핑
    한글: DB에 저장된 실제 컬럼명
    영어: 계산 함수에서 사용할 변수명
    """
    
    # DB 한글 컬럼 → 영어 인자명 매핑
    COLUMN_MAPPING = {
        "sodium": "나트륨(mg)",  # 나트륨 (mg)
        "sugar": "당류(g)",  # 당류 (g)
        "carbohydrate": "탄수화물(g)",  # 탄수화물 (g)
        "potassium": "칼륨(mg)",  # 칼륨 (mg)
        "protein": "단백질(g)",  # 단백질 (g)
        "phosphorus": "인(mg)",  # 인 (mg)
        "fat": "지방(g)",  # 지방 (g)
        "calories": "에너지(kcal)",  # 에너지 (kcal)
        "fiber": "식이섬유(g)",  # 식이섬유 (g)
    }
    
    # DB에서 실제 존재하는 컬럼명 (현재 JSON_DB 기준)
    DB_ACTUAL_COLUMNS = {
        "sodium": "sodium",
        "sugar": "sugar",
        "carbohydrate": "carbohydrate",
        "potassium": "potassium",
        "protein": "protein",
        "phosphorus": "phosphorus",
        "fat": "fat",
        "calories": "calories",
        "fiber": "fiber",  # DB에 없을 수 있으므로 기본값 필요
    }
    
    @staticmethod
    def get_db_column(english_name: str) -> str:
        """영어 인자명으로 DB 컬럼명 조회"""
        return ColumnMapper.DB_ACTUAL_COLUMNS.get(english_name, english_name)
    
    @staticmethod
    def map_product_to_dict(product: Dict[str, Any]) -> Dict[str, float]:
        """
        DB의 product를 영어 변수명 dict로 변환
        """
        mapped = {}
        for eng_name, db_col in ColumnMapper.DB_ACTUAL_COLUMNS.items():
            mapped[eng_name] = product.get(db_col, 0)
        return mapped


# ============================================================================
# 3. 질병별 SCORING 함수들
# ============================================================================

class DiseaseScoring:
    """
    질병별 점수 산정 알고리즘
    각 함수는 영어 변수명 dict를 받아 0-100 점수 반환
    """
    
    @staticmethod
    def calculate_hypertension_score(nutrients: Dict[str, float]) -> float:
        """
        고혈압 점수 산정 (Michaelis-Menten 곡선 기반)
        
        칼륨(K): 최소 섭취량(3500mg)까지 급격히 상승, 
                권장 섭취량(4700mg) 이상은 수렴 (5점 내외 차이)
        나트륨(Na): Na/K 비율에 고혈압 환자 민감도 가중치(w=3)를 적용하여 감점
        
        Score_K = V_max × K / (C_k + K)
        Score   = Score_K - (Na/K × w × C)
        """
        k_mg = nutrients.get("potassium", 0)
        na_mg = nutrients.get("sodium", 0)
        
        V_max = 102   # 이론적 점수 최대치
        C_k = 150     # 반포화 상수 (4700mg 이상 수렴 유도)
        w = 3         # 고혈압 환자 민감도 가중치 (일반인 대비 2.9배 → 보수적 3배)
        C = 10        # 스케일 보정 상수
        
        if k_mg <= 0:
            return 0
        
        # 1. 칼륨 점수 (Michaelis-Menten 곡선)
        score_k = min(V_max * (k_mg / (C_k + k_mg)), 100)
        
        # 2. Na/K 비율 기반 감점
        penalty = (na_mg / k_mg) * w * C if k_mg > 0 else 0
        
        # 3. 최종 점수 (0점 미만은 0점 처리)
        final_score = score_k - penalty
        
        return max(0, final_score)
    
    @staticmethod
    def calculate_diabetes_score(nutrients: Dict[str, float]) -> float:
        """
        당뇨병 점수 산정
        
        순탄수화물(Net Carbs) = 총탄수 - (식이섬유)
        순탄수 열량 비중(R_cal) = (net_carb × 4 / kcal) × 100
        당류 비중(R_sugar) = (sugar / net_carb) × 100
        
        최종 점수 = 100 - (0.6 × R_cal + 0.4 × R_sugar)
        페널티: R_sugar > 10%이면 -15점
        """
        carb = nutrients.get("carbohydrate", 0)
        sugar = nutrients.get("sugar", 0)
        fiber = nutrients.get("fiber", 0)
        kcal = nutrients.get("calories", 0)
        
        # 순탄수화물 계산
        net_carb = max(sugar, carb - fiber)
        
        if kcal <= 0 or net_carb <= 0:
            return 0
        
        # 순탄수 열량 비중
        r_cal = (net_carb * 4 / kcal) * 100
        
        # 당류 비중
        r_sugar = (sugar / net_carb) * 100
        
        # 최종 점수 산정 (0-100)
        w1, w2 = 0.6, 0.4
        score = 100 - (w1 * r_cal + w2 * r_sugar)
        
        # 페널티: 당류 비율이 10%를 초과할 경우 -15점
        if r_sugar > 10:
            score -= 15
        
        return max(0, score)
    
    @staticmethod
    def calculate_kidney_disease_score(
        nutrients: Dict[str, float],
        kidney_stage: str = "CKD_3_5",
        is_processed_food: bool = False,
        weight: Optional[float] = None
    ) -> float:
        """
        신장질환 점수 산정 (Michaelis-Menten 기반 다항식 곡선)
        
        영양소 별 점수 계산:
        1. 나트륨: Hill 방정식 (지수=10)
        2. 칼륨: 신장 단계별 Hill 방정식 (CKD vs HD vs PD)
        3. 인: 가공식품 여부 반영
        4. 단백질: 신장 단계별 기준 (사용자 체중 기반)
        
        최종 점수: (0.7 × max score) + (0.3 × average score)
        
        Args:
            nutrients: Dict[str, float] - 영양소 정보
            kidney_stage: str - 신장질환 단계
                - "CKD_3_5": CKD 3-5단계 (투석 전)
                - "HD": Hemodialysis (혈액투석)
                - "PD": Peritoneal Dialysis (복막투석)
            is_processed_food: bool - 가공식품 여부 (인 흡수율 1.5배)
            weight: Optional[float] - 사용자 체중(kg) (단백질 계산 필요)
            
        Returns:
            float - 0-100 범위의 신장질환 건강 점수
        """
        na_mg = nutrients.get("sodium", 0)
        k_mg = nutrients.get("potassium", 0)
        phos_mg = nutrients.get("phosphorus", 0)
        protein_g = nutrients.get("protein", 0)
        
        # ====================================================================
        # 1. 나트륨 점수 (Hill 방정식, n=10)
        # Stock_Na = min(139.5 * (x^10 / (730^10 + x^10)), 100)
        # ====================================================================
        x_na = na_mg
        score_na = min(139.5 * (x_na ** 10 / (730 ** 10 + x_na ** 10)), 100)
        
        # ====================================================================
        # 2. 칼륨 점수 (신장 단계별 Hill 방정식, n=5)
        # ====================================================================
        x_k = k_mg
        
        if kidney_stage == "CKD_3_5":
            # CKD 3-5단계: Hill 방정식 (n=5, K_m=420)
            score_k = min(141.8 * (x_k ** 5 / (420 ** 5 + x_k ** 5)), 100)
        elif kidney_stage == "HD":
            # 혈액투석: Hill 방정식 (n=5, K_m=550)
            score_k = min(140.2 * (x_k ** 5 / (550 ** 5 + x_k ** 5)), 100)
        elif kidney_stage == "PD":
            # 복막투석: Michaelis-Menten (n=1, K_m=150)
            score_k = min(102 * (x_k / (150 + x_k)), 100)
        else:
            # 기본값 (CKD 3-5)
            score_k = min(141.8 * (x_k ** 5 / (420 ** 5 + x_k ** 5)), 100)
        
        # ====================================================================
        # 3. 인 점수 (가공식품 보정 적용, Hill 방정식 n=6)
        # effective_p = (is_processed_food) ? x * 1.5 : x
        # Score_P = 118.8 * (effective_p^6 / (250^6 + effective_p^6))
        # ====================================================================
        x_p = phos_mg
        effective_p = x_p * 1.5 if is_processed_food else x_p
        score_p = 118.8 * (effective_p ** 6 / (250 ** 6 + effective_p ** 6))
        
        # ====================================================================
        # 4. 단백질 점수 (체중 기반, 신장 단계별)
        # ====================================================================
        x_pr = protein_g
        
        if weight is None or weight <= 0:
            # weight 정보가 없으면 중립값
            score_pr = 50.0
        elif kidney_stage == "CKD_3_5":
            # CKD 3-5단계: 일일 총 단백질 = 0.6 * weight(kg)
            # 한끼 섭취량 = (0.6 * weight) / 3
            # L_meal = (0.6 * weight) / 3
            # K = L_meal * 0.85
            # C = 100 * (K^n + L_meal^n) / (L_meal^n) where n=2
            # raw_score = C * (protein_g^n) / (K^n + protein_g^n)
            # Score_Pr = min(raw_score, 100.0)
            
            n = 2
            l_meal = (0.6 * weight) / 3.0
            k = l_meal * 0.85
            
            if l_meal > 0:
                c = 100 * ((k ** n + l_meal ** n) / (l_meal ** n))
                raw_score = c * (x_pr ** n) / (k ** n + x_pr ** n)
                score_pr = min(raw_score, 100.0)
            else:
                score_pr = 50.0
        
        elif kidney_stage in ["HD", "PD"]:
            # 혈액투석/복막투석: 일일 총 단백질 = 1.2 * weight(kg)
            # 한끼 섭취량 = (1.2 * weight) / 3
            # T = (1.2 * weight_kg) / 3.0
            # raw_score = 100 * ((protein_g - T) / T) ** 2
            # Score_Pr = min(raw_score, 100.0)
            
            t = (1.2 * weight) / 3.0
            
            if t > 0:
                raw_score = 100 * ((x_pr - t) / t) ** 2
                score_pr = min(raw_score, 100.0)
            else:
                score_pr = 50.0
        
        else:
            # 기본값
            score_pr = 50.0
        
        # ====================================================================
        # 5. 최종 점수 계산
        # riskScore_kidney = (0.7 × max(scores)) + (0.3 × average(scores))
        # ====================================================================
        riskscores = [score_na, score_k, score_p, score_pr]
        max_riskscore = max(riskscores)
        avg_riskscore = sum(riskscores) / len(riskscores)
        
        final_score = 100 - ((0.7 * max_riskscore) + (0.3 * avg_riskscore))
        
        return max(0, min(final_score, 100))


# ============================================================================
# 4. 메인 Sub-Recommendation 클래스
# ============================================================================

class SubstitutionReco:
    """
    대체 상품 추천 에이전트
    
    동작 흐름:
    1. overallState에서 질병 플래그 읽기
    2. Candidate에서 product_id 리스트 가져오기
    3. DB에서 각 product의 성분 조회
    4. 질병별 scoring 계산
    5. 기존 product 대비 점수 높은 상품 추천
    """
    
    def __init__(self, products_db: Dict[str, Any]):
        """
        Args:
            products_db: DB의 products 테이블 (Dict[product_id, product_data])
        """
        self.products_db = products_db
        self.mapper = ColumnMapper()
        self.scoring = DiseaseScoring()
    
    def get_product_nutrients(self, product_id: str) -> Dict[str, float]:
        """
        DB에서 product_id에 해당하는 영양소 정보 조회 후 매핑
        
        Args:
            product_id: 조회할 상품 ID
            
        Returns:
            영어 인자명으로 정렬된 영양소 Dict
        """
        product = self.products_db.get(str(product_id), {})
        
        if not product:
            return {}
        
        return self.mapper.map_product_to_dict(product)
    
    def calculate_health_score(
        self,
        product_id: str,
        disease_type: str,
        kidney_stage: str = "CKD_3_5",
        is_processed_food: bool = False,
        weight: Optional[float] = None
    ) -> float:
        """
        제품의 질병별 건강 점수 계산
        
        Args:
            product_id: 상품 ID
            disease_type: 질병 타입 ('diabetes', 'hypertension', 'kidney_disease')
            kidney_stage: 신장질환 단계 (기본값: "CKD_3_5")
                - "CKD_3_5": CKD 3-5단계 (투석 전)
                - "HD": Hemodialysis (혈액투석)
                - "PD": Peritoneal Dialysis (복막투석)
            is_processed_food: 가공식품 여부 (기본값: False)
            weight: 사용자 체중(kg) (신장질환 단백질 계산용)
            
        Returns:
            0-100 범위의 점수
        """
        nutrients = self.get_product_nutrients(product_id)
        
        if not nutrients:
            return 0
        
        if disease_type == "diabetes":
            return self.scoring.calculate_diabetes_score(nutrients)
        elif disease_type == "hypertension":
            return self.scoring.calculate_hypertension_score(nutrients)
        elif disease_type == "kidney_disease":
            return self.scoring.calculate_kidney_disease_score(
                nutrients,
                kidney_stage=kidney_stage,
                is_processed_food=is_processed_food,
                weight=weight
            )
        else:
            return 50  # 기본값

    def calculate_health_scores(
        self,
        product_id: str,
        state: Dict[str, Any]
    ) -> Dict[str, float]:
        """
        overallState에 설정된 질병 플래그(=1)만 선택하여, 해당 질병들의 건강 점수를 일괄 계산합니다.

        Args:
            product_id: 상품 ID (str)
            state: overallState(dict). 예: {"user_profile": {"diabetes_flag": 1, ...}}

        Returns:
            Dict[str, float]: 활성화된 질병에 대해서만 {disease_type: score} 형태로 반환
        """
        nutrients = self.get_product_nutrients(product_id)
        if not nutrients:
            return {}

        user_profile = state.get("user_profile", {}) if isinstance(state, dict) else {}

        results: Dict[str, float] = {}

        # 당뇨병
        if user_profile.get("diabetes_flag") == 1:
            results["diabetes"] = self.scoring.calculate_diabetes_score(nutrients)

        # 고혈압
        if user_profile.get("hypertension_flag") == 1:
            results["hypertension"] = self.scoring.calculate_hypertension_score(nutrients)

        # 신장질환
        if user_profile.get("kidneydisease_flag") == 1:
            # 병증별 옵션은 overallState(user_profile)에 저장된 값을 우선 사용
            kidney_detail = user_profile.get("kidney_detail", "CKD_3_5")
            processed = user_profile.get("is_processed_food", False)
            weight = user_profile.get("weight")

            results["kidney_disease"] = self.scoring.calculate_kidney_disease_score(
                nutrients,
                kidney_stage=str(kidney_detail),
                is_processed_food=bool(processed),
                weight=weight if (isinstance(weight, (int, float)) and weight > 0) else None,
            )

        return results
    
    def validate_swap(
        self,
        chosen_product_id: str,
        recommended_product_id: str,
        disease_type: str,
        kidney_stage: str = "CKD_3_5",
        is_processed_food: bool = False,
        weight: Optional[float] = None
    ) -> bool:
        """
        추천 상품이 선택 상품보다 점수상 우수한지 검증
        
        Args:
            chosen_product_id: 사용자가 선택한 상품
            recommended_product_id: 추천할 상품
            disease_type: 질병 타입
            kidney_stage: 신장질환 단계 (기본값: "CKD_3_5")
            is_processed_food: 가공식품 여부 (기본값: False)
            weight: 사용자 체중(kg)
            
        Returns:
            True if recommended score > chosen score
        """
        chosen_score = self.calculate_health_score(
            chosen_product_id,
            disease_type,
            kidney_stage=kidney_stage,
            is_processed_food=is_processed_food,
            weight=weight
        )
        recommended_score = self.calculate_health_score(
            recommended_product_id,
            disease_type,
            kidney_stage=kidney_stage,
            is_processed_food=is_processed_food,
            weight=weight
        )
        
        return recommended_score > chosen_score
    
    def generate_recommendations(
        self,
        state: Dict[str, Any],
        candidates: List[Candidate],
        kidney_stage: str = "CKD_3_5",
        is_processed_food: bool = False,
        weight: Optional[float] = None
    ) -> List[SubRecommendation]:
        """
        overallState와 Candidate 리스트를 기반으로 추천 생성
        
        Args:
            state: overallState (질병 플래그 포함)
            candidates: reco_agent에서 전달한 후보 상품 리스트
            kidney_stage: 신장질환 단계 (기본값: "CKD_3_5")
                - "CKD_3_5": CKD 3-5단계
                - "HD": Hemodialysis
                - "PD": Peritoneal Dialysis
            is_processed_food: 가공식품 여부 (기본값: False)
            weight: 사용자 체중(kg)
            
        Returns:
            SubRecommendation 리스트
        """
        recommendations = []
        
        # 1. overallState에서 질병 플래그 추출
        user_profile = state.get("user_profile", {})
        
        diseases_to_check = []
        
        if user_profile.get("diabetes_flag") == 1:
            diseases_to_check.append("diabetes")
        
        if user_profile.get("hypertension_flag") == 1:
            diseases_to_check.append("hypertension")
        
        if user_profile.get("kidneydisease_flag") == 1:
            diseases_to_check.append("kidney_disease")
        
        # 2. 질병이 없으면 빈 리스트 반환
        if not diseases_to_check:
            return recommendations
        
        # 3. 각 질병과 Candidate별로 점수 계산
        for disease_type in diseases_to_check:
            for candidate in candidates:
                product_id = str(candidate["product_id"])
                rank = candidate["rank"]
                
                # 해당 질병에 대한 점수 계산
                if disease_type == "kidney_disease":
                    score = self.calculate_health_score(
                        product_id,
                        disease_type,
                        kidney_stage=kidney_stage,
                        is_processed_food=is_processed_food,
                        weight=weight
                    )
                else:
                    score = self.calculate_health_score(product_id, disease_type)
                
                product = self.products_db.get(product_id, {})
                product_name = product.get("name", f"Product {product_id}")
                
                recommendation = SubRecommendation(
                    product_id=int(product_id),
                    rank=rank,
                    disease_type=disease_type,
                    score=score,
                    reason=f"{disease_type.upper()} 건강 점수: {score:.1f}/100"
                )
                
                recommendations.append(recommendation)
        
        # 4. 점수 순으로 정렬 (높은 순)
        recommendations.sort(key=lambda x: x["score"], reverse=True)
        
        return recommendations

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        LangGraph 파이프라인에서 호출할 수 있는 Node 래퍼 메서드.
        state 객체 내부의 값이나 reco_agent에서 생성된 후보 리스트 등을 
        추출하여 generate_recommendations를 실행하고 결과를 state에 병합하여 반환합니다.
        """
        # reco_agent에서 만든 후보 상품 추출 (가정: state["candidates"])
        # 만약 state 구조에서 다른 키를 사용한다면 그에 맞게 수정 필요
        candidates = state.get("candidates", [])
        
        if not candidates:
            print("[Sub-Reco] 전달받은 Candidate가 없어 추천을 생성할 수 없습니다.")
            state["sub_recommendations"] = []
            return state

        # user_profile이 state에 없다면 직접 state를 사용하도록 fallback
        user_profile = state.get("user_profile", state)

        # 필요한 추가 파라미터들
        kidney_stage = user_profile.get("kidney_detail", "CKD_3_5")
        is_processed_food = user_profile.get("is_processed_food", False)
        weight = user_profile.get("weight")

        print("\n[Sub-Reco] 대체 상품 추천 계산 중...")
        recos = self.generate_recommendations(
            state=state,
            candidates=candidates,
            kidney_stage=kidney_stage,
            is_processed_food=is_processed_food,
            weight=weight
        )
        
        # 결과를 state에 저장
        state["sub_recommendations"] = recos
        state["next_step"] = "resp_agent"  # 다음으로 넘어갈 에이전트 지정
        print(f"[Sub-Reco] 대안 상품 추천 완료 (총 {len(recos)}개)")
        
        return state


# ============================================================================
# 5. LLM 프롬프트 생성
# ============================================================================

class LLMPromptGenerator:
    """
    Sub-Recommendation 결과를 기반으로 LLM용 프롬프트 생성
    """
    
    @staticmethod
    def generate_substitution_prompt(chosen_product: Dict[str, Any],
                                   recommended_product: Dict[str, Any],
                                   disease_type: str,
                                   score_difference: float) -> Dict[str, Any]:
        """
        대체 상품 추천 팝업용 프롬프트 생성
        
        Args:
            chosen_product: 사용자가 선택한 상품 정보
            recommended_product: 추천할 상품 정보
            disease_type: 질병 타입
            score_difference: 점수 차이
            
        Returns:
            LLM 지시사항이 포함된 Dict
        """
        
        disease_names = {
            "diabetes": "당뇨병",
            "hypertension": "고혈압",
            "kidney_disease": "신장질환"
        }
        
        disease_name = disease_names.get(disease_type, disease_type)
        
        prompt = {
            "action": "DISPLAY_WARNING_SUBSTITUTION",
            "context": f"사용자가 {disease_name} 환자입니다. 선택한 상품: {chosen_product.get('name')}",
            "chosen_product": {
                "name": chosen_product.get("name"),
                "product_id": chosen_product.get("product_id")
            },
            "recommended_product": {
                "name": recommended_product.get("name"),
                "product_id": recommended_product.get("product_id")
            },
            "disease_type": disease_type,
            "score_improvement": score_difference,
            "llm_instruction": f"""
당신은 임상영양사입니다. 다음 정보를 바탕으로 친절하지만 설득력 있는 상품 변경 메시지를 생성하세요.

선택된 상품: {chosen_product.get('name')}
추천 상품: {recommended_product.get('name')}
질병: {disease_name}
점수 개선도: {score_difference:.1f}점

메시지는 다음 형식으로 작성하세요:
[WARNING] 또는 [추천]으로 시작하여 1-2 문장으로 이유를 설명하세요. 
과학적 근거를 기반으로 친절한 톤을 유지하세요.
"""
        }
        
        return prompt
    
    @staticmethod
    def generate_suitability_prompt(product: Dict[str, Any],
                                  disease_type: str,
                                  score: float) -> Dict[str, Any]:
        """
        상품 적합성 평가 프롬프트 생성
        
        Args:
            product: 상품 정보
            disease_type: 질병 타입
            score: 건강 점수
            
        Returns:
            LLM 지시사항이 포함된 Dict
        """
        
        disease_names = {
            "diabetes": "당뇨병",
            "hypertension": "고혈압",
            "kidney_disease": "신장질환"
        }
        
        disease_name = disease_names.get(disease_type, disease_type)
        
        # 점수에 따른 등급 결정
        if score >= 80:
            grade = "[우수] 매우 좋은 선택입니다"
        elif score >= 60:
            grade = "[양호] 무난한 선택입니다"
        elif score >= 40:
            grade = "[주의] 적절한 대체 상품을 찾아보세요"
        else:
            grade = "[경고] 이 상품은 피하는 것이 좋습니다"
        
        prompt = {
            "action": "DISPLAY_SUITABILITY",
            "context": f"사용자가 {disease_name} 환자입니다.",
            "product": {
                "name": product.get("name"),
                "product_id": product.get("product_id")
            },
            "disease_type": disease_type,
            "health_score": score,
            "grade": grade,
            "llm_instruction": f"""
당신은 임상영양사입니다. 다음 상품의 {disease_name} 환자에 대한 적합성을 평가하세요.

상품명: {product.get('name')}
건강 점수: {score}/100
평가등급: {grade}

다음 형식으로 메시지를 작성하세요:
{grade}
이유: 1-2 문장으로 과학적 근거를 제시하세요.
"""
        }
        
        return prompt