def generate_final_profile(user_id, user_diseases, user_weight):
    # 1. 질환별 임계값 설정 (Data Dictionary)
    # 수치 뒤의 'g', 'mg' 등의 단위는 계산 편의를 위해 생략합니다.
    disease_thresholds = {
        "allergy": {
            "restricted_ingredients": ["milk", "egg", "peanut", "nuts", "soy", "wheat", "fish", "shellfish"]
        },
        "kidneydisease_pre_dialysis": {  # CKD 3-5단계 (투석 전)
            "protein": 0.60 * weight, # kg당 계산
            "sodium": 2300,
            "phosphorus": 1000,
            "calcium": 1000,
            "kcal": 35 * weight
        },
        "kidneydisease_dialysis": {      # CKD 5단계 (투석)
            "protein": 1.2 * weight,
            "sodium": 2300,
            "potassium": 2000,
            "phosphorus": 1000,
            "calcium": 1000,
            "kcal": 35 * weight
        },
        "diabetes": {
            "sugar": 5
        },
        "hypertension": {
            "sodium": 2300,
            "potassium_min": 3500, # > 3500mg
            "fat_ratio": 0.25      # 총 열량의 25% 이하
        }
    }

    # 2. 우선순위 맵 (낮을수록 높음)
    priority_map = {
        "allergy": 1,
        "kidneydisease": 2,
        "diabetes": 3,
        "hypertension": 4
    }

    # 3. 사용자가 가진 질환 필터링 및 우선순위 정렬
    # 예: user_diseases = {"diabetes": 1, "kidneydisease": 1}
    active_diseases = [d for d, active in user_diseases.items() if active == 1]
    sorted_diseases = sorted(active_diseases, key=lambda x: priority_map.get(x, 99))

    # 4. Final Profile 생성 (Priority-Merger)
    final_profile = {
        "user_id": user_id,
        "restricted_ingredients": []
    }

    for disease in sorted_diseases:
        # 신장병의 경우 세부 단계(투석 여부)에 따른 분기 처리가 필요할 수 있습니다.
        # 여기서는 예시로 pre_dialysis를 기본값으로 사용합니다.
        lookup_key = "kidneydisease_pre_dialysis" if disease == "kidneydisease" else disease
        thresholds = disease_thresholds.get(lookup_key, {})

        for nutrient, value in thresholds.items():
            # 알러지 유발 물질 문자열 처리
            if nutrient == "restricted_ingredients":
                # 중복 없이 추가
                final_profile["restricted_ingredients"] = list(set(final_profile["restricted_ingredients"] + value))

            # 성분 임계값 처리: 이미 등록된 성분은 무시 (우선순위 보호)
            elif nutrient not in final_profile:
                final_profile[nutrient] = value

    return final_profile