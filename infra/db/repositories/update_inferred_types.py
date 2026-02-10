# ==========================================
# [C] 🛠️ 실행: 데이터 업데이트 및 사용자 검증
# ==========================================

print("--- [1] 제품 데이터 업데이트 (inferred_types 추가) ---")
for pid, p_data in products.items():
    # 1. 영양성분 기반 태그 자동 생성
    auto_tags = analyze_nutrient_claims(p_data)
    
    # 2. 기존 태그(원재료 기반)와 병합 (중복 제거)
    current_tags = p_data.get('inferred_types', [])
    updated_tags = list(set(current_tags + auto_tags))
    
    # 3. 데이터 업데이트
    products[pid]['inferred_types'] = updated_tags
    print(f"[{p_data['name']}] 태그: {updated_tags}")


print("\n--- [2] 질환별 사용자 맞춤 분석 시뮬레이션 ---")

# 시나리오: 60kg의 신장병 환자와 당뇨 환자가 제품을 조회함
analyzer = DiseaseAnalyzer(user_weight=60)
target_products = ["201104000001", "201104000003", "201905000000"] # 스테이크, 믹스너트, 김부각

for pid in products:
    product = products[pid]
    print(f"\n>>> 제품 분석: {product['name']}")
    
    # Case 1: 만성콩팥병 환자 (투석 전)
    safe_kidney, msg_kidney = analyzer.check_kidney_pre_dialysis(product)
    status_kidney = "✅안전" if safe_kidney else "❌위험"
    print(f"  [투석 전 신장병 환자]: {status_kidney} -> {', '.join(msg_kidney)}")

    # Case 1-2: 만성콩팥병 (투석 후)
    safe_kidneypost, msg_post = analyzer.check_kidney_dialysis(product)
    status_kidneypost = "✅안전" if safe_kidneypost else "❌위험"
    print(f"  [투석 후 신장병 환자]: {status_kidneypost} -> {', '.join(msg_post)}")

    # Case 2: 당뇨 환자
    safe_diabetes, msg_diabetes = analyzer.check_diabetes(product)
    status_diabetes = "✅안전" if safe_diabetes else "❌위험"
    print(f"  [당뇨 환자]  : {status_diabetes} -> {', '.join(msg_diabetes)}")
    
    # Case 3: 고혈압 환자
    safe_bp, msg_bp = analyzer.check_hypertension(product)
    status_bp = "✅안전" if safe_bp else "❌위험"
    print(f"  [고혈압 환자]: {status_bp} -> {', '.join(msg_bp)}")