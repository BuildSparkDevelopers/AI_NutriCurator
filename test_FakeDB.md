# test_FakeDB 작업 기록

## 목적

LangGraph가 FakeDB로 동작 가능한지 점검하고, 필요한 수정 포인트를 문서화한다.

---

## 1) 1차 분석 결과

초기 분석 시점 기준으로 다음 문제가 확인되었다.

1. `langgraph` import 실패 가능
   - 실행 환경에서 `langgraph` 미설치 시 `ModuleNotFoundError` 발생
2. `reco_agent` import 단계 오류
   - 파일 하단 실행 코드/전역 참조(`FAKE_DB`)로 인해 import 시점 실패 가능
3. 그래프 wiring 불일치
   - `graph.py`가 참조하는 클래스/노드와 실제 구현 정합성 부족
4. 데이터 소스 분기 부재
   - `api/deps.py`가 Postgres 경로를 고정 사용
5. state 계약 불일치 가능성
   - `*_flag`, `final_profile`, `candidates` 등 키 사용이 에이전트별로 불균일

---

## 2) 수행했던 코드 작업 (이후 워킹트리 정리됨)

다음 변경을 실제로 적용하고 문법 점검까지 수행했었다.

### A. FakeDB 분기 및 로더 추가

- `app/settings.py`
  - `AI_DATA_SOURCE` 설정 필드 추가 (`postgres` / `fake`)
- `api/deps.py`
  - `get_user_service`, `get_product_service`에 fake/postgres 분기 추가
- 신규 파일
  - `infra/db/fake_data.py` (FAKE_DB 로더)
  - `infra/db/repositories/fake_user_repo.py`
  - `infra/db/repositories/fake_health_repo.py`
  - `infra/db/repositories/fake_product_repo.py`

### B. LangGraph 노드 정합성 보완

- `ai/orchestrator/graph.py`
  - fake 데이터 주입 기반으로 에이전트 초기화 정리
  - 오케스트레이터 노드 래핑(`next_step` 반환)
  - 노드/엣지 연결 구조 정리
- `ai/orchestrator/policy.py`
  - `threshold_checked` 기준 추가로 chat loop 방지
- `ai/agents/chat_core_agent.py`
  - `evaluate_threshold`에서 `threshold_checked = True` 세팅

### C. API state 보강

- `api/routes/ai.py`
  - `user_profile`에 `diabetes_flag`, `hypertension_flag`, `kidneydisease_flag`, `allergy_flag` 보강

### D. 문법/린트 점검

- `py_compile` 기반 문법 점검 수행
- 변경 파일 대상 lints 점검 수행

---

## 3) 작업 중 확인된 이슈

`ai/agents/user_agent.py`는 과거 코드가 중복 삽입된 상태로 보였고,
정리 과정에서 파일 충돌 가능성이 높아 대체 모듈(`user_agent_node.py`) 경로로 우회 적용했었다.

---

## 4) 워킹트리 정리 이력 (완료)

사용자 요청에 따라 워킹트리를 정리했다.

- 실행:
  - `git reset --hard HEAD`
  - `git clean -fd`
- 결과:
  - 모든 로컬 수정/추가 파일 제거
  - `git status --short` 기준 clean 상태 확인

즉, 위 2번 항목의 코드 변경은 **현재 저장소에는 남아있지 않다**.

---

## 5) 현재 상태 요약

현재 저장소는 clean 상태이며, FakeDB 적용 코드는 반영되어 있지 않다.  
다시 진행하려면 아래 순서로 재적용하면 된다.

1. `AI_DATA_SOURCE` 설정 추가
2. FakeDB 로더 + fake repositories 추가
3. `api/deps.py` 분기 적용
4. `graph.py` 및 policy/chat state 흐름 정합화
5. import/컴파일/E2E 검증

---

## 6) 재적용 시 권장 체크리스트

- [ ] `python -c "import langgraph"` 성공
- [ ] `python -c "from ai.orchestrator.graph import compile_graph; compile_graph()"` 성공
- [ ] fake 모드(`AI_DATA_SOURCE=fake`)에서 `/api/v1/ai/analyze` 응답 확인
- [ ] 응답의 `full_state_debug`에 `next_step`, `sub_recommendations`, `final_answer` 확인

# LangGraph FakeDB 동작 점검 정리

## 목적

`langgraph` 파이프라인이 실제 Postgres 대신 `fakeDB`를 사용해 정상 동작할 수 있는지 점검하고, 필요한 수정 지점을 파일 단위로 정리한다.

---

## 1) 현재 상태 진단 결과

### 핵심 결론

현재 코드는 **FakeDB 적용 이전에 런타임/구조 이슈로 먼저 실패**한다.  
즉, FakeDB 연결만 추가해도 바로 동작하는 상태는 아니다.

### 실행/검증에서 확인된 실제 문제

1. `langgraph` 모듈 import 실패
   - `ai/orchestrator/graph.py` import 시 `ModuleNotFoundError: No module named 'langgraph'`
2. `reco_agent` import 시 `FAKE_DB` 미정의
   - `ai/agents/reco_agent.py`에서 모듈 import 단계에서 `NameError` 발생
3. 그래프 참조 클래스 불일치
   - `graph.py`는 `Recommendation`, `ResponseGeneration`을 import하지만 실제 구현 정합성이 맞지 않거나 파일이 없음
4. API 데이터 진입점은 Postgres 고정
   - `api/routes/ai.py`는 `Depends(get_user_service/get_product_service)` 경로를 타며, 현재 DI 구성은 SQLAlchemy 기반 Repository 고정

---

## 2) 주요 원인 분석

### A. 의존성/환경 불일치

- `requirements.txt`에는 `langgraph`가 있으나, 실행 환경에 설치되지 않은 상태
- `user_agent.py`가 사용하는 `langchain_core`는 실행 환경에서 import 실패 확인됨

### B. 에이전트 파일의 모듈 레벨 실행 코드

- `ai/agents/reco_agent.py` 하단에 예시 실행 코드가 남아 있어 import 시점에 `FAKE_DB` 참조
- 실서비스에서는 모듈 import만 되어야 하는데, 파일 로드 시 실제 실행이 일어나는 구조

### C. 그래프 노드 wiring과 실제 구현의 계약 불일치

- `graph.py`가 노드로 연결하는 클래스/메서드와 실제 에이전트 구현이 완전히 맞물리지 않음
- 생성자 시그니처(`SubstitutionReco(products_db)`) 및 반환 state 계약(`candidates`, `sub_recommendations`) 정렬 필요

### D. 데이터 소스 분기 부재

- `api/deps.py`가 현재 Postgres만 주입
- FakeDB를 선택할 수 있는 설정 플래그 및 분기 로직 부재

---

## 3) FakeDB 동작을 위한 변경 포인트 (파일별)

## 3.1 의존성/환경

### `requirements.txt`

- `langgraph` 설치 상태 보장
- 필요 시 아래 의존성 추가/정리
  - `langchain-core`
  - `langchain-openai` (실제 사용 시)

### 실행 단계

- `pip install -r requirements.txt` 재실행 후 import 검증 필요

---

## 3.2 FakeDB 로딩 계층 추가

### 권장 신규 파일

- `infra/db/fake_db.py` 또는 `infra/db/fake_loader.py`

### 해야 할 일

1. 현재 `infra/db/FAKE_DB.json`은 JSON 형식이 아니라 파이썬 리터럴 형식이므로 파싱 방식 결정
   - 방법 1: `.py` 모듈로 전환해 직접 import
   - 방법 2: 진짜 JSON으로 변환 후 `json.load` 사용
2. 최소 인터페이스 제공
   - `get_user_profile(user_id)`
   - `get_product(product_id)`
   - `list_products()` 또는 reco용 전체 products

---

## 3.3 DI 분기 추가 (postgres vs fake)

### `app/settings.py`

- 예: `AI_DATA_SOURCE` 설정 추가
  - `"postgres"` / `"fake"` 중 선택

### `api/deps.py`

- `get_user_service`, `get_product_service`에서 설정값 기반 분기
  - `postgres`: 기존 SQLAlchemy Repository 주입
  - `fake`: FakeRepository/FakeService 주입

### 기대 효과

- `/api/v1/ai/analyze` 호출 시 코드 수정 없이 설정만으로 데이터 소스 전환 가능

---

## 3.4 LangGraph wiring 정합성 수정

### `ai/orchestrator/graph.py`

- 실제 존재/사용 가능한 에이전트만 import하도록 정리
- 각 노드 생성자 인자 주입 방식 통일
  - 예: `SubstitutionReco(products_db=...)`
- `model=None` 같은 placeholder 초기화 제거 또는 안전한 mock 주입

### `ai/agents/reco_agent.py`

- 모듈 하단 실행 예시 코드 제거
  - `engine = RecoEngine(...)`
  - `print(...)`
- LangGraph 노드 계약 함수(`run(state)->state`) 중심으로 재구성

### `ai/agents/user_agent.py`

- 하단 예제 실행 코드 제거
- 반환 키를 `overallState`와 통일
  - `diabetes_flag`, `hypertension_flag`, `kidneydisease_flag`, `allergy_flag`

### `ai/agents/sub_reco_agent.py`

- 입력을 `state["candidates"]`로 받을 경우 reco 노드에서 동일 키로 반드시 세팅
- 출력은 `state["sub_recommendations"]`로 명확히 고정

---

## 3.5 State 계약 통일

### `ai/state/schema.py` + 각 agent 반환값

- 단일 계약 유지:
  - reco 출력: `candidates`
  - sub_reco 출력: `sub_recommendations`
  - 사용자 플래그: `*_flag` 계열
- `user_profile` vs `final_profile` 중 하나 선택 후 전체 통일

---

## 4) 권장 적용 순서

1. 의존성 설치/정리 (`langgraph`, `langchain-core` 등)
2. FakeDB 로더 + Fake repo/service 계층 추가
3. `api/deps.py`에 데이터 소스 분기 구현
4. `graph.py` import/노드 wiring 정리
5. `reco_agent`, `user_agent` 모듈 하단 실행 코드 제거
6. state 계약 통일 후 `/api/v1/ai/analyze` E2E 검증

---

## 5) 검증 체크리스트

- [ ] `python -c "from ai.orchestrator.graph import compile_graph; compile_graph()"`
- [ ] `python -c "import ai.agents.reco_agent"` import 에러 없음
- [ ] `python -c "import ai.agents.user_agent_node"` import 에러 없음
- [ ] fake 모드에서 `/api/v1/ai/analyze` 호출 시 DB 연결 없이 응답 반환
- [ ] 응답 내 `full_state_debug`에 `candidates`, `sub_recommendations`, `final_answer` 기대값 포함

---

## 6) 최종 정리

현재 이슈의 본질은 "FakeDB 미연결" 단일 문제가 아니라,  
**(1) 런타임 import 실패 + (2) 그래프/에이전트 계약 불일치 + (3) DI 분기 부재**의 복합 문제다.

따라서 우선순위는 아래와 같다.

1. import/환경 정상화
2. 그래프/에이전트 계약 정렬
3. FakeDB 분기 도입
4. 통합 테스트

이 순서로 진행하면 FakeDB 기반 LangGraph 테스트가 안정적으로 가능해진다.
