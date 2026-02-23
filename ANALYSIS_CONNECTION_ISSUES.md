# 🔴 Agent 연결 상태 분석 보고서

## 요약
**심각도: 🔴 CRITICAL** - Policy.py와 AI agents 간에 **데이터 흐름 단절** 및 **타입 불일치 다수 발견**

---

## 1. 🔴 critical 병목 #1: LangGraph 구조 오류

### 문제
#### langgrapharchitecture.py (Line 1203-1210)
```python
workflow.add_node("orch_agent", user_agent_func)      # ❌ 모두 같은 함수!
workflow.add_node("user_agent", user_agent_func)
workflow.add_node("chat_agent", user_agent_func)
workflow.add_node("reco_agent", user_agent_func)
workflow.add_node("sub_reco_agent", user_agent_func)
workflow.add_node("resp_agent", user_agent_func)
```

**문제점:**
- 모든 노드가 동일한 `user_agent_func`를 실행함
- 각 agent의 실제 구현 로직이 **완전히 무시됨**
- reco-agent의 RecoEngine 또는 sub-reco_agent의 SubstitutionReco 클래스가 **호출되지 않음**

### 영향
- ❌ chat_core_agent.py의 evaluate_threshold() 미실행
- ❌ reco-agent.py의 retrieve_candidates_v1() 미실행  
- ❌ sub-reco_agent.py의 DiseaseScoring 계산 미실행
- 📊 **결과: 모든 agent가 동일한 함수를 반복 실행 (무한 루프 위험)**

### 해결 방안
```python
from ai.agents.user_agent import ProfileRetrieval
from ai.agents.chat_core_agent import EvidenceGeneration
from ai.agents.reco_agent import reco_node
from ai.agents.sub_reco_agent import SubstitutionReco

workflow.add_node("orch_agent", orchestrator.run)      # ✅ 정의된 함수들
workflow.add_node("user_agent", user_agent_instance.run)
workflow.add_node("chat_agent", chat_agent_instance.evaluate_threshold)
workflow.add_node("reco_agent", lambda state: reco_node(state, engine))
workflow.add_node("sub_reco_agent", sub_reco_instance.generate_recommendations)
```

---

## 2. 🟠 MAJOR 병목 #2: Policy RouterLogic과 State 불일치

### 문제점 A: "user_profile" vs "final_profile"

#### policy.py (Line 7)
```python
u_profile = state.get("user_profile", {})  # ❌ 찾고 있는 필드
```

#### langgrapharchitecture.py (Line 80)
```python
class overallState(TypedDict):
    # ...
    final_profile: dict  # ✅ 실제 정의된 필드
```

**문제:** Policy가 존재하지 않는 필드 요청 → **항상 빈 dict {} 반환**

### 문제점 B: Flag 데이터 구조 모호

#### policy.py (Line 13-14)
```python
flag_keys = ["diabetes_flag", "hypertension_flag", "kidneydisease_flag", "allergy_flag"]
flags = [u_profile.get(key, state.get(key)) for key in flag_keys]
```

**문제:**
- `u_profile`이 빈 dict라면 `state.get(key)`로 폴백됨
- **하지만 overallState 정의상 이 필드들은 state의 루트에 존재해야 함**
- 일부는 `user_profile` 안에, 일부는 state 루트에 있을 수 있는 혼란 야기

### 데이터 흐름 추적
```
user_agent.run() 반환 → state 업데이트
  ↓
policy.run() 호출 → state.get("user_profile", {}) = {} (실패!)
  ↓
flag_keys = [None, None, None, None] (모두 NULL)
  ↓
"규칙 1" 트리거: "필수 건강 정보(Flags) 일부 누락" → user_agent로 다시 돌아감
  ↓
💫 무한 루프 또는 조기 종료
```

---

## 3. 🟠 MAJOR 병목 #3: Agent 상태 반환값 타입 불일치

### 3.1 user_agent.py - Field Name 오류

#### 실제 반환값 (Line 99-110)
```python
return {
    "name": user_profile["name"],
    "diabetes": user_profile["diabetes_flag"],        # ❌ "diabetes_flag" 아님
    "hypertension": user_profile["hypertension_flag"],
    "kidneydisease": user_profile["kidneydisease_flag"],
    "allergy": user_profile["allergy_flag"],
    
    "diabetes_type": user_profile["diabetes_detail"],  # ❌ "diabetes_detail" 아님
    "hypertension_type": user_profile["hypertension_detail"],
    "kidneydisease_type": user_profile["kidneydisease_detail"],
    "allergy_list": user_profile["allergy_list"],
    "final_profile": user_profile,
    "next_step": "orch_agent"
}
```

#### overallState 정의 (Line 66-85)
```python
class overallState(TypedDict):
    # Expected fields:
    diabetes_flag: int                          # ❌ user_agent는 "diabetes" 반환
    hypertension_flag: int
    kidneydisease_flag: int
    allergy_flag: int
    diabetes_detail: Literal[...]               # ❌ user_agent는 "diabetes_type" 반환
    hypertension_detail: Literal[...]
    kidney_detail: Literal[...]
    # ... 12개 추가 필드 누락됨
```

**영향:** Policy가 "diabetes_flag" 요청 → user_agent는 "diabetes" 반환 → Policy가 찾지 못함

### 3.2 chat_core_agent.py - 불완전한 상태 초기화

#### 실제 반환값 (Line 209-213)
```python
state: overallState = {
    "any_allergen": False,
    "substitute": []
}
```

#### 문제:
- **12개의 필수 필드 누락:** user_id, product_id, name, diabetes_flag, hypertension_flag, etc.
- overallState의 required fields 손실 → downstream agents에서 KeyError 가능

### 3.3 reco-agent.py - 독자적 State 스키마

#### reco-agent.py (Line 267-283)
```python
class RecoState(TypedDict):
    clicked_product_id: int
    k: int
    weights: List[float]
    reco_to_sub: RecoToSubPayload      # ←overallState와 완전히 다른 구조
    reco_debug: Dict[str, Any]
    error: Optional[str]
```

**문제:**
- overallState와 **타입 완전 불일치**
- LangGraph workflow에서 state 병합 불가능
- reco_agent 입력/출력 데이터 구조 불명확

### 3.4 sub-reco_agent.py - 노드 함수 부재

#### 문제:
- `run()` 메서드가 정의되지 않음
- workflow에서 호출 불가능 (add_node에 연결할 메서드 없음)
- generate_recommendations()는 내부 메서드일 뿐 LangGraph 노드가 아님

---

## 4. 🟡 MEDIUM 병목 #4: Workflow Edge 구성 오류

### 문제: add_conditional_edges 키 존재하지 않음

#### langgrapharchitecture.py (Line 1228-1236)
```python
workflow.add_conditional_edges(
    "orch_agent",
    lambda x: x["next_step"],
    {
        "user_agent": "user_agent_node",      # ❌ 이 노드들이 없음!
        "chat_agent": "chat_agent_node",
        "reco_agent": "reco_agent_node",
        "end": END
    }
)
```

### 실제 존재하는 노드
```
❌ "user_agent_node"      (존재하지 않음)
✅ "user_agent"          (존재함)
❌ "chat_agent_node"     (존재하지 않음)
✅ "chat_agent"          (존재함)
```

**영향:** conditional edge 매핑 실패 → workflow 실행 불가능

---

## 5. 🟡 MEDIUM 병목 #5: 데이터 타입 검증 부재

### policy.py의 느슨한 타입 처리

```python
flags = [u_profile.get(key, state.get(key)) for key in flag_keys]
flag_sum = sum(int(f) for f in flags)  # ❌ f가 None이면 int(None) → 에러
```

### 위험 시나리오
```python
# flags = [None, None, None, None]
flag_sum = sum(int(f) for f in flags)  # ❌ TypeError: int() argument must be a string or a number
```

---

## 6. 데이터 흐름 시각화 (현재 상태)

```
START → orch_agent
         ↓
    policy.run()
         ↓
    state.get("user_profile", {}) = {}  ❌ 빈 dict
         ↓
    flags = [None, None, None, None]    ❌ 모두 NULL
         ↓
    "규칙 1 트리거" (필수 정보 누락)
         ↓
    return "user_agent"
         ↓
user_agent_func() ← **다시 user_agent_func 호출! 💫 무한루프**
         ↓
    반환: {"diabetes": 1, ...}  ❌ 필드명 불일치
         ↓
    state 병합 실패 OR 덮어쓰기 발생
```

---

## 🔁 실제 타입 불일치 매핑표

| Field | overallState | user_agent 반환 | chat_core_agent | policy 요구 |
|-------|-------------|-----------------|-----------------|-----------|
| 당뇨 플래그 | `diabetes_flag` | `diabetes` | ❌ | `diabetes_flag` |
| 고혈압 플래그 | `hypertension_flag` | `hypertension` | ❌ | `hypertension_flag` |
| 신장 플래그 | `kidneydisease_flag` | `kidneydisease` | ❌ | `kidneydisease_flag` |
| 알러지 플래그 | `allergy_flag` | `allergy` | ❌ | `allergy_flag` |
| 당뇨 상세 | `diabetes_detail` | `diabetes_type` | ❌ | ❌ |
| 신장 상세 | `kidney_detail` | `kidneydisease_type` | ❌ | ❌ |
| 프로필 | `final_profile` | `final_profile` | ❌ | `user_profile` |

---

## 📋 종합 병목 우선순위

| 순위 | 병목 | 심각도 | 영향 범위 | 예상 복구시간 |
|------|------|--------|---------|-----------|
| 1️⃣ | LangGraph add_node 오류 | 🔴 CRITICAL | entire workflow | 1시간 |
| 2️⃣ | policy-state 필드 불일치 | 🔴 CRITICAL | policy + all agents | 1.5시간 |
| 3️⃣ | agent 반환값 타입 불일치 | 🟠 MAJOR | all agents | 3시간 |
| 4️⃣ | sub-reco_agent 노드 미구현 | 🟠 MAJOR | recommendation pipeline | 2시간 |
| 5️⃣ | conditional_edges 키 오류 | 🟡 MEDIUM | edge routing | 30분 |
| 6️⃣ | 타입 검증 부재 | 🟡 MEDIUM | runtime errors | 1시간 |

---

## ✅ 권장 수정 순서

1. **즉시:** overallState 정의와 모든 agent 반환값 통일
2. **즉시:** langgrapharchitecture.py의 add_node() 수정  
3. **우선:** conditional_edges 키 이름 수정
4. **우선:** sub-reco_agent의 LangGraph 노드 함수 생성
5. **필요:** policy.py의 상태 추출 로직 재작성
6. **필요:** 타입 검증 로직 추가

---

## 🎯 Current Data Flow vs Expected

### ❌ 현재
```
orch_agent → user_agent_func → user_agent_func → ... (무한 루프)
```

### ✅ 필요한 형태
```
START 
  ↓
orch_agent (policy.run) 
  ├→ if flags_valid → user_agent.run()
  ├→ if has_disease → chat_agent.evaluate_threshold()
  ├→ if exceed_found → reco_agent.run()
  ├→ ├→ sub_reco_agent.generate_recommendations()
  ├→ ├→ resp_agent.format_response()
  ↓
END
```

