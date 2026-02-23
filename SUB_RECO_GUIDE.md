# Sub-Recommendation Agent (Sub-Reco) 사용 설명서

## 개요

**Sub-Reco Agent**는 사용자의 건강 상태(질병 플래그)를 기반으로 선택한 상품의 영양 점수를 계산하고, 더 나은 대체 상품을 추천하는 시스템입니다.

### 주요 특징

✅ **질병별 지능형 Scoring**: 고혈압, 당뇨병, 신장질환 각각에 최적화된 점수 계산  
✅ **DB 자동 매핑**: 한글 DB 컬럼을 영어 코드와 자동 연결  
✅ **과학적 알고리즘**: Michaelis-Menten 곡선 등 영양학 기반 계산  
✅ **LLM 연동**: 결과를 바탕으로 LLM용 프롬프트 자동 생성

---

## 파일 구조

```
ai/agents/
├── sub-reco_agent.py          # Main agent 파일
├── chat_core_agent.py         # Chat agent
├── user_agent.py              # User agent
├── __init__.py
└── orchestrator/
    └── policy.py              # Router logic
```

---

## 주요 클래스 & 함수

### 1. `Candidate` (TypedDict)

reco_agent에서 전달받는 상품 후보

```python
class Candidate(TypedDict):
    product_id: int    # 상품 ID
    rank: int          # 순위
```

### 2. `SubRecommendation` (TypedDict)

Sub-Reco Agent가 반환하는 추천 결과

```python
class SubRecommendation(TypedDict):
    product_id: int       # 상품 ID
    rank: int             # 순위
    disease_type: str     # 질병 타입
    score: float          # 건강 점수 (0-100)
    reason: str           # 추천 이유
```

### 3. `ColumnMapper` (클래스)

한글 DB 컬럼과 영어 코드 변수 간 매핑

```python
# 사용 예시
mapper = ColumnMapper()
nutrients = mapper.map_product_to_dict(product)
# {
#     "sodium": 180,
#     "sugar": 1,
#     "carbohydrate": 20,
#     ...
# }
```

**DB 컬럼 매핑 정보**:

| 영어 변수      | DB 컬럼명    | 단위 |
| -------------- | ------------ | ---- |
| `sodium`       | sodium       | mg   |
| `sugar`        | sugar        | g    |
| `carbohydrate` | carbohydrate | g    |
| `potassium`    | potassium    | mg   |
| `protein`      | protein      | g    |
| `phosphorus`   | phosphorus   | mg   |
| `fat`          | fat          | g    |
| `calories`     | calories     | kcal |
| `fiber`        | fiber        | g    |

### 4. `DiseaseScoring` (클래스)

질병별 점수 계산 알고리즘

#### 4.1 고혈압 점수 (Michaelis-Menten 곡선)

```python
score = DiseaseScoring.calculate_hypertension_score(nutrients)
```

**수식**:
$$\text{Score}_K = V_{max} \times \frac{K}{C_k + K}$$
$$\text{Penalty} = \frac{Na}{K} \times w \times C$$
$$\text{Final Score} = \text{Score}_K - \text{Penalty}$$

**매개변수**:

- $V_{max} = 102$ (이론적 최대값)
- $C_k = 150$ (반포화 상수)
- $w = 3$ (고혈압 환자 민감도 가중치)
- $C = 10$ (스케일 보정 상수)

**영향 인자**:

- ☑️ 칼륨(K): 높을수록 점수 ↑
- ☑️ 나트륨(Na): 높을수록 점수 ↓

---

#### 4.2 당뇨병 점수

```python
score = DiseaseScoring.calculate_diabetes_score(nutrients)
```

**수식**:
$$\text{Net Carbs} = \max(\text{sugar}, \text{carb} - \text{fiber})$$
$$R_{cal} = \frac{\text{net\_carb} \times 4}{\text{kcal}} \times 100$$
$$R_{sugar} = \frac{\text{sugar}}{\text{net\_carb}} \times 100$$
$$\text{Score} = 100 - (0.6 \times R_{cal} + 0.4 \times R_{sugar})$$

**페널티**: $R_{sugar} > 10\%$ → -15점

---

#### 4.3 신장질환 점수

```python
score = DiseaseScoring.calculate_kidney_disease_score(nutrients)
```

**감점 기준**:

- 나트륨: 100mg마다 -2점
- 인(P): 50mg마다 -3점
- 칼륨(K): 100mg마다 -2점

---

### 5. `SubstitutionReco` (메인 클래스)

대체 상품 추천 에이전트

#### 초기화

```python
from ai.agents.sub_reco_agent import SubstitutionReco

# DB에서 products 테이블 로드
products_db = {...}  # Dict[product_id, product_data]

reco = SubstitutionReco(products_db)
```

#### 5.1 개별 제품 점수 계산

```python
score = reco.calculate_health_score(product_id, disease_type)

# 예시
score = reco.calculate_health_score("0", "hypertension")  # 결과: 34.3
```

**Parameters**:

- `product_id` (str): DB의 상품 ID
- `disease_type` (str): `"diabetes"`, `"hypertension"`, `"kidney_disease"`

**Return**: float (0-100 범위)

---

#### 5.2 제품 영양 정보 조회

```python
nutrients = reco.get_product_nutrients(product_id)
# {
#     "sodium": 180,
#     "sugar": 1,
#     "carbohydrate": 20,
#     ...
# }
```

---

#### 5.3 대체 상품 검증 (Swap Validation)

```python
is_valid = reco.validate_swap(chosen_id, recommended_id, disease_type)

# 예시: 고들빼기김치 → 아몬드맛 (고혈압)
is_valid = reco.validate_swap("2", "1", "hypertension")  # True
```

**동작**:

- 추천 상품의 점수 > 선택 상품의 점수 → `True`
- 그 외 → `False`

---

#### 5.4 추천 생성 (핵심 함수)

```python
recommendations = reco.generate_recommendations(state, candidates)
```

**Parameters**:

1. `state` (Dict): overallState 객체

   ```python
   {
       "user_profile": {
           "diabetes_flag": 1,         # 당뇨병 있음
           "hypertension_flag": 0,     # 고혈압 없음
           "kidneydisease_flag": 0,    # 신장질환 없음
           "allergy_flag": 0
       }
   }
   ```

2. `candidates` (List[Candidate]): reco_agent에서 전달받은 상품 리스트
   ```python
   [
       {"product_id": 0, "rank": 1},
       {"product_id": 1, "rank": 2},
       {"product_id": 2, "rank": 3}
   ]
   ```

**Return**: List[SubRecommendation]

```python
[
    {
        "product_id": 1,
        "rank": 2,
        "disease_type": "diabetes",
        "score": 75.5,
        "reason": "DIABETES 건강 점수: 75.5/100"
    },
    ...
]
```

**동작 흐름**:

1. State에서 질병 플래그 추출
2. 각 질병별로 Candidate 상품 점수 계산
3. 점수 높은 순으로 정렬
4. SubRecommendation 리스트 반환

---

### 6. `LLMPromptGenerator` (클래스)

LLM용 프롬프트 생성

#### 6.1 대체 상품 추천 프롬프트

```python
prompt = LLMPromptGenerator.generate_substitution_prompt(
    chosen_product,      # Dict
    recommended_product, # Dict
    disease_type,        # str
    score_difference     # float
)
```

**반환 구조**:

```python
{
    "action": "DISPLAY_WARNING_SUBSTITUTION",
    "context": "사용자가 고혈압 환자입니다. 선택한 상품: ...",
    "chosen_product": {"name": "...", "product_id": "..."},
    "recommended_product": {"name": "...", "product_id": "..."},
    "disease_type": "hypertension",
    "score_improvement": 34.3,
    "llm_instruction": "당신은 임상영양사입니다. ..."
}
```

---

#### 6.2 적합성 평가 프롬프트

```python
prompt = LLMPromptGenerator.generate_suitability_prompt(
    product,      # Dict
    disease_type, # str
    score         # float
)
```

**반환 구조**:

```python
{
    "action": "DISPLAY_SUITABILITY",
    "context": "사용자가 당뇨병 환자입니다.",
    "product": {"name": "...", "product_id": "..."},
    "disease_type": "diabetes",
    "health_score": 75.5,
    "grade": "[우수] 매우 좋은 선택입니다",
    "llm_instruction": "당신은 임상영양사입니다. ..."
}
```

**점수 등급**:

- 80점 이상: `[우수] 매우 좋은 선택입니다`
- 60~79점: `[양호] 무난한 선택입니다`
- 40~59점: `[주의] 적절한 대체 상품을 찾아보세요`
- 40점 미만: `[경고] 이 상품은 피하는 것이 좋습니다`

---

## 사용 예시

### 예시 1: 고혈압 환자 상품 추천

```python
from ai.agents.sub_reco_agent import SubstitutionReco, LLMPromptGenerator
import json

# 1. DB에서 상품 로드 (pseudo code)
products_db = load_from_json_db()

# 2. Sub-Reco 초기화
reco = SubstitutionReco(products_db)

# 3. 사용자 상태
state = {
    "user_profile": {
        "diabetes_flag": 0,
        "hypertension_flag": 1,      # 고혈압 환자
        "kidneydisease_flag": 0,
        "allergy_flag": 0
    }
}

# 4. reco_agent에서 받은 후보
candidates = [
    {"product_id": 0, "rank": 1},
    {"product_id": 1, "rank": 2},
    {"product_id": 2, "rank": 3}
]

# 5. 추천 생성
recommendations = reco.generate_recommendations(state, candidates)

# 6. 최상위 추천 상품
top_recommendation = recommendations[0]
product_id = str(top_recommendation["product_id"])
chosen_product = PRODUCTS_DB.get("2")  # 사용자가 선택한 상품

# 7. Swap 검증
if reco.validate_swap("2", product_id, "hypertension"):
    score_diff = top_recommendation["score"] - reco.calculate_health_score("2", "hypertension")

    # 8. LLM 프롬프트 생성
    prompt = LLMPromptGenerator.generate_substitution_prompt(
        chosen_product,
        products_db[product_id],
        "hypertension",
        score_diff
    )

    print(json.dumps(prompt, ensure_ascii=False, indent=2))
```

**출력 예시**:

```json
{
  "action": "DISPLAY_WARNING_SUBSTITUTION",
  "context": "사용자가 고혈압 환자입니다. 선택한 상품: 고들빼기김치",
  "chosen_product": {
    "name": "고들빼기김치",
    "product_id": "201804000002"
  },
  "recommended_product": {
    "name": "설화눈꽃팝김부각스낵 아몬드맛",
    "product_id": "201804000001"
  },
  "disease_type": "hypertension",
  "score_improvement": 34.3,
  "llm_instruction": "당신은 임상영양사입니다..."
}
```

---

## LangGraph 통합

### State 흐름

```
[User Agent] (질병 플래그 설정)
    ↓
[Chat Agent] (영양 초과 체크)
    ↓
[Sub-Reco Agent] ← 여기에서 Sub-Reco 실행
    │
    ├─ overallState 읽기 (질병 플래그)
    ├─ Candidate 조회 (reco_agent)
    ├─ DB product 조회 (컬럼 매핑)
    ├─ 질병별 scoring 계산
    └─ SubRecommendation 저장
    ↓
[LLM] (프롬프트로 팝업 생성)
    ↓
사용자
```

---

## 주의사항

⚠️ **DB 컬럼명 주의**

- DB의 컬럼명이 변경되면 `ColumnMapper.DB_ACTUAL_COLUMNS`를 업데이트해야 합니다.

⚠️ **질병 플래그 형식**

- `int` 타입 (0 또는 1)만 지원

⚠️ **상품 ID**

- `product_id`는 String으로 변환하여 DB 조회

⚠️ **점수 범위**

- 모든 질병의 점수는 0-100 범위

---

## 향후 개선 사항

- [ ] 복합 질병 상호작용 반영 (고혈압 + 당뇨 시너지)
- [ ] 사용자 체중 기반 단백질 제한값 동적 계산
- [ ] 알러지 정보 포함
- [ ] 계절성 식품 데이터베이스
- [ ] A/B 테스트용 점수 가중치 조정

---

## 문의 사항

이 문서에 대한 질문이나 개선 제안은 개발팀에 연락주시기 바랍니다.
