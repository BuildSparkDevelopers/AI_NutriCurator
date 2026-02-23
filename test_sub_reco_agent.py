# -*- coding: utf-8 -*-
"""
Sub-Reco-Agent 테스트 코드
"""

import json
import sys
sys.path.insert(0, '/workspaces/AI_NutriCurator')

from ai.agents.sub_reco_agent import (
    SubstitutionReco, ColumnMapper, DiseaseScoring, 
    Candidate, SubRecommendation, LLMPromptGenerator
)

# ============================================================================
# 테스트용 DB 데이터
# ============================================================================

PRODUCTS_DB = {
    "0": {
        "product_id": "201905000000",
        "name": "설화눈꽃팝김부각스낵",
        "calories": 150,
        "sodium": 180,
        "carbohydrate": 20,
        "sugar": 1,
        "fat": 7,
        "protein": 2,
        "phosphorus": 45,
        "potassium": 120,
        "fiber": 2
    },
    "1": {
        "product_id": "201804000001",
        "name": "설화눈꽃팝김부각스낵 아몬드맛",
        "calories": 170,
        "sodium": 160,
        "carbohydrate": 18,
        "sugar": 1,
        "fat": 10,
        "protein": 4,
        "phosphorus": 80,
        "potassium": 200,
        "fiber": 1
    },
    "2": {
        "product_id": "201804000002",
        "name": "고들빼기김치",
        "calories": 45,
        "sodium": 850,
        "carbohydrate": 8,
        "sugar": 4,
        "fat": 0.5,
        "protein": 2,
        "phosphorus": 35,
        "potassium": 320,
        "fiber": 1
    },
    "3": {
        "product_id": "199504000000",
        "name": "해태 허니버터칩",
        "calories": 345,
        "sodium": 350,
        "carbohydrate": 30,
        "sugar": 7,
        "fat": 23,
        "protein": 3,
        "phosphorus": 70,
        "potassium": 450,
        "fiber": 0
    }
}

CANDIDATES = [
    {"product_id": 0, "rank": 1},
    {"product_id": 1, "rank": 2},
    {"product_id": 2, "rank": 3},
    {"product_id": 3, "rank": 4}
]

# 고혈압 환자 상태
STATE_HYPERTENSION = {
    "user_profile": {
        "diabetes_flag": 0,
        "hypertension_flag": 1,
        "kidneydisease_flag": 0,
        "allergy_flag": 0
    }
}

# 당뇨병 환자 상태
STATE_DIABETES = {
    "user_profile": {
        "diabetes_flag": 1,
        "hypertension_flag": 0,
        "kidneydisease_flag": 0,
        "allergy_flag": 0
    }
}

# 신장질환 환자 상태
STATE_KIDNEY = {
    "user_profile": {
        "diabetes_flag": 0,
        "hypertension_flag": 0,
        "kidneydisease_flag": 1,
        "allergy_flag": 0
    }
}

# ============================================================================
# 테스트 함수
# ============================================================================

def test_column_mapper():
    """Column Mapper 테스트"""
    print("\n" + "="*70)
    print("✓ 테스트 1: Column Mapper")
    print("="*70)
    
    mapper = ColumnMapper()
    product = PRODUCTS_DB["0"]
    
    mapped = mapper.map_product_to_dict(product)
    print(f"\n원본 product: {product}")
    print(f"\n매핑된 dict: {mapped}")
    print(f"\n✅ 매핑 성공: sodium={mapped['sodium']}, sugar={mapped['sugar']}")


def test_disease_scoring():
    """질병별 scoring 함수 테스트"""
    print("\n" + "="*70)
    print("✓ 테스트 2: 질병별 Scoring")
    print("="*70)
    
    mapper = ColumnMapper()
    scoring = DiseaseScoring()
    
    for product_key in ["0", "1", "2", "3"]:
        product = PRODUCTS_DB[product_key]
        nutrients = mapper.map_product_to_dict(product)
        
        hyper_score = scoring.calculate_hypertension_score(nutrients)
        diabetes_score = scoring.calculate_diabetes_score(nutrients)
        kidney_score = scoring.calculate_kidney_disease_score(nutrients)
        
        print(f"\n상품: {product['name']}")
        print(f"  - 고혈압 점수: {hyper_score:.1f}/100")
        print(f"  - 당뇨병 점수: {diabetes_score:.1f}/100")
        print(f"  - 신장질환 점수: {kidney_score:.1f}/100")


def test_substitution_reco():
    """SubstitutionReco 클래스 테스트"""
    print("\n" + "="*70)
    print("✓ 테스트 3: SubstitutionReco 클래스")
    print("="*70)
    
    reco = SubstitutionReco(PRODUCTS_DB)
    
    # 개별 제품의 점수 계산
    print("\n--- 개별 제품 점수 계산 ---")
    for product_key in ["0", "1", "2"]:
        score_hyper = reco.calculate_health_score(product_key, "hypertension")
        score_diabetes = reco.calculate_health_score(product_key, "diabetes")
        score_kidney = reco.calculate_health_score(product_key, "kidney_disease")
        
        product_name = PRODUCTS_DB[product_key]["name"]
        print(f"\n{product_name}")
        print(f"  고혈압: {score_hyper:.1f}/100")
        print(f"  당뇨: {score_diabetes:.1f}/100")
        print(f"  신장: {score_kidney:.1f}/100")


def test_generate_recommendations():
    """추천 생성 테스트"""
    print("\n" + "="*70)
    print("✓ 테스트 4: 추천 생성 (generate_recommendations)")
    print("="*70)
    
    reco = SubstitutionReco(PRODUCTS_DB)
    
    # 고혈압 환자
    print("\n--- 고혈압 환자 추천 ---")
    hyper_recs = reco.generate_recommendations(STATE_HYPERTENSION, CANDIDATES)
    for rec in hyper_recs:
        product = PRODUCTS_DB[str(rec["product_id"])]
        print(f"  {product['name']}: {rec['score']:.1f}/100 ({rec['reason']})")
    
    # 당뇨병 환자
    print("\n--- 당뇨병 환자 추천 ---")
    diabetes_recs = reco.generate_recommendations(STATE_DIABETES, CANDIDATES)
    for rec in diabetes_recs:
        product = PRODUCTS_DB[str(rec["product_id"])]
        print(f"  {product['name']}: {rec['score']:.1f}/100 ({rec['reason']})")
    
    # 신장질환 환자
    print("\n--- 신장질환 환자 추천 ---")
    kidney_recs = reco.generate_recommendations(STATE_KIDNEY, CANDIDATES)
    for rec in kidney_recs:
        product = PRODUCTS_DB[str(rec["product_id"])]
        print(f"  {product['name']}: {rec['score']:.1f}/100 ({rec['reason']})")


def test_validate_swap():
    """Swap 검증 테스트"""
    print("\n" + "="*70)
    print("✓ 테스트 5: Swap 검증 (validate_swap)")
    print("="*70)
    
    reco = SubstitutionReco(PRODUCTS_DB)
    
    # 상품 0 vs 상품 1 (고혈압)
    is_valid = reco.validate_swap("0", "1", "hypertension")
    print(f"\n고혈압: {PRODUCTS_DB['0']['name']} → {PRODUCTS_DB['1']['name']}: {is_valid}")
    
    # 상품 1 vs 상품 2 (당뇨)
    is_valid = reco.validate_swap("1", "2", "diabetes")
    print(f"당뇨: {PRODUCTS_DB['1']['name']} → {PRODUCTS_DB['2']['name']}: {is_valid}")
    
    # 상품 3 vs 상품 0 (신장질환)
    is_valid = reco.validate_swap("3", "0", "kidney_disease")
    print(f"신장: {PRODUCTS_DB['3']['name']} → {PRODUCTS_DB['0']['name']}: {is_valid}")


def test_llm_prompt_generator():
    """LLM 프롬프트 생성 테스트"""
    print("\n" + "="*70)
    print("✓ 테스트 6: LLM 프롬프트 생성")
    print("="*70)
    
    chosen = PRODUCTS_DB["3"]
    recommended = PRODUCTS_DB["0"]
    
    # 대체 프롬프트
    print("\n--- 대체 상품 추천 프롬프트 ---")
    prompt = LLMPromptGenerator.generate_substitution_prompt(
        chosen, recommended, "hypertension", 65.3
    )
    print(json.dumps(prompt, indent=2, ensure_ascii=False))
    
    # 적합성 평가 프롬프트
    print("\n--- 적합성 평가 프롬프트 ---")
    suitability_prompt = LLMPromptGenerator.generate_suitability_prompt(
        chosen, "diabetes", 35.5
    )
    print(json.dumps(suitability_prompt, indent=2, ensure_ascii=False))


def test_multiple_diseases():
    """복수 질병 환자 테스트"""
    print("\n" + "="*70)
    print("✓ 테스트 7: 복수 질병 환자 추천")
    print("="*70)
    
    reco = SubstitutionReco(PRODUCTS_DB)
    
    # 고혈압 + 당뇨
    multi_state = {
        "user_profile": {
            "diabetes_flag": 1,
            "hypertension_flag": 1,
            "kidneydisease_flag": 0,
            "allergy_flag": 0
        }
    }
    
    recs = reco.generate_recommendations(multi_state, CANDIDATES)
    
    print(f"\n고혈압 + 당뇨 환자 (총 {len(recs)}개 추천):")
    for rec in recs:
        product = PRODUCTS_DB[str(rec["product_id"])]
        print(f"  {rec['disease_type'].upper()}: {product['name']} - {rec['score']:.1f}/100")


# ============================================================================
# 메인 실행
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("AI NutriCurator - Sub-Recommendation Agent 테스트")
    print("="*70)
    
    try:
        test_column_mapper()
        test_disease_scoring()
        test_substitution_reco()
        test_generate_recommendations()
        test_validate_swap()
        test_llm_prompt_generator()
        test_multiple_diseases()
        
        print("\n" + "="*70)
        print("✅ 모든 테스트 완료!")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
