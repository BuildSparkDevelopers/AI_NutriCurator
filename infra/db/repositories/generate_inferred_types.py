# ==========================================
# [A] 🥗 영양성분 정적 판별 로직 (DB 저장용)
# ==========================================
def analyze_nutrient_claims(product):
    tags = []
    
    # 데이터 추출 (없으면 0)
    sugar = product.get('sugar', 0)
    protein = product.get('protein', 0)
    fat = product.get('fat', 0)
    sodium = product.get('sodium', 0)
    carb = product.get('carbohydrate', 0)
    potassium = product.get('potassium', 0)
    
    # 1. 당류 (Sugar)
    if sugar < 0.5: tags.append("zero_sugar")
    elif sugar <= 5: tags.append("low_sugar")
    elif sugar >= 15: tags.append("high_sugar") # 추가

    # 2. 단백질 (Protein)
    if protein >= 10: tags.append("high_protein")
    
    # 3. 지방 (Fat)
    if fat <= 3: tags.append("low_fat")
    elif fat >= 15: tags.append("high_fat")
    
    # 4. 나트륨 (Sodium)
    if sodium <= 120: tags.append("low_sodium")
    elif sodium >= 600: tags.append("high_sodium") # 고나트륨 기준
    
    # 5. 칼륨 (Potassium)
    if potassium >= 500: tags.append("high_potassium")
    
    # 6. 탄수화물 (Carb)
    if carb >= 50: tags.append("high_carb")

    return tags

# ==========================================
# [B] 🏥 질환별 맞춤 영양 분석기 (실시간 분석용)
# ==========================================
class DiseaseAnalyzer:
    def __init__(self, user_weight=60):
        self.user_weight = user_weight

    def check_kidney_pre_dialysis(self, product):
        """만성콩팥병 (투석 전): 단백질, 나트륨, 칼륨, 인 제한"""
        warnings = []
        is_safe = True
        
        # 단백질: 간식 1회 8g 이하 권장
        if product.get('protein', 0) > 8:
            warnings.append(f"단백질 주의({product.get('protein')}g)")
            is_safe = False
            
        # 나트륨: 400mg 이하
        if product.get('sodium', 0) > 400:
            warnings.append(f"나트륨 위험({product.get('sodium')}mg)")
            is_safe = False
            
        # 칼륨/인: 200mg 이하 (엄격)
        if product.get('potassium', 0) > 200:
            warnings.append(f"칼륨 위험({product.get('potassium')}mg)")
            is_safe = False
        if product.get('phosphorus', 0) > 150:
            warnings.append(f"인 위험({product.get('phosphorus')}mg)")
            is_safe = False
            
        return is_safe, warnings

    def check_kidney_dialysis(self, product):
        """
        [만성콩팥병 (투석 후)]
        - 특징: 단백질 권장(X 제한안함), 나트륨/칼륨/인 여전히 엄격 제한
        """
        warnings = []
        is_safe = True
        
        # 1. 단백질: 투석 환자는 단백질 손실이 커서 제한하지 않음 (오히려 권장)
        # 따라서 단백질이 높다고 경고를 주지 않습니다.
        
        # 2. 나트륨: 갈증 유발 및 혈압 상승 (400mg 제한)
        if product.get('sodium', 0) > 400:
            warnings.append(f"나트륨 주의({product.get('sodium')}mg)")
            is_safe = False
            
        # 3. 칼륨: 심장마비 위험 (200mg 제한 - 매우 엄격)
        if product.get('potassium', 0) > 200:
            warnings.append(f"칼륨 위험({product.get('potassium')}mg)")
            is_safe = False

        # 4. 인: 뼈 질환 및 석회화 위험 (150mg 제한 - 매우 엄격)
        if product.get('phosphorus', 0) > 150:
            warnings.append(f"인 위험({product.get('phosphorus')}mg)")
            is_safe = False
            
        return is_safe, warnings

    def check_diabetes(self, product):
        """당뇨: 당류, 탄수화물 제한"""
        warnings = []
        is_safe = True
        
        if product.get('sugar', 0) > 5:
            warnings.append(f"당류 높음({product.get('sugar')}g)")
            is_safe = False
            
        if product.get('carbohydrate', 0) > 30:
            warnings.append(f"탄수화물 과다({product.get('carbohydrate')}g)")
            is_safe = False
            
        return is_safe, warnings

    def check_hypertension(self, product):
        """고혈압: 나트륨 제한"""
        warnings = []
        is_safe = True
        
        if product.get('sodium', 0) > 400:
            warnings.append(f"나트륨 높음({product.get('sodium')}mg)")
            is_safe = False
            
        return is_safe, warnings