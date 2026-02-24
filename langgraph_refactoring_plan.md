# 🏗️ `langgrapharchitecture.py` 구조 분석 및 분리 계획

`langgrapharchitecture.py` 파일은 초기 Jupyter Notebook 환경에서 작성된 코드를 스크립트화한 것으로 보이며, 현재 **DB 데이터, 도메인 로직, AI 모델 선언, LangGraph 오케스트레이션 코드가 하나의 파일에 혼재**되어 있습니다. 
`프로젝트폴더구조.md`의 아키텍처 원칙(역할 분리)에 맞게 각 요소를 분리하고 삭제해야 할 방향성을 정리했습니다.

---

## 1️⃣ 코드 역할별 분류

현재 파일(`langgrapharchitecture.py`)에 존재하는 항목들을 4가지 코어 역할로 분류했습니다.

### 🔴 1. 다른 파일에 이미 존재하는 코드 (중복/대체 가능)
이 부분은 이미 다른 모듈(Agents)이나 설정 파일에 존재하므로 **삭제 또는 완전히 교체**되어야 합니다.

- **에이전트 Mock 클래스 로직**
  - `RouterLogic`, `ProfileRetrieval`, `EvidenceGeneration1` 클래스들
  - *이유:* `ai/orchestrator/policy.py`, `ai/agents/user_agent.py`, `ai/agents/chat_core_agent.py` 등 모듈화된 파일에 이미 실제 로직이 구현되어 있습니다.
- **LLM 모델 로드 및 프롬프트 로직**
  - `Qwen2.5` 로드 (`AutoModelForCausalLM`, `AutoTokenizer`), `ChatOpenAI` 선언부
  - `generate_allergy_prompt1` 등 하드코딩된 프롬프트 로직
  - *이유:* 환경변수 관리 블록(`app/settings.py` 또는 `infra/llm/client.py`)과 각 Agent 내부로 이관되어야 합니다.

### 🟡 2. DB 및 데이터 관련 코드 (이동 필요)
임시로 정의된 Mock 데이터와 매핑 테이블로, 실제 DB 조회 로직이나 스키마 정의 파일로 이동해야 합니다.

- **Mock 데이터 딕셔너리**
  - `products`, `final_profiles`
  - *이유:* `scripts/seed_demo_data.py` (초기 데이터 삽입용) 또는 `tests/` 디렉토리의 Mock 데이터로 이동해야 하며, 실제 운영 코드에서는 `infra/db/repositories/`를 통해 DB에서 조회해야 합니다.
- **식품 성분 매핑 및 임계값 테이블**
  - `FOOD_DB_MAPPER`
  - `generate_final_profile` 내의 `disease_thresholds` 
  - `allergy_substitution_rules`
  - *이유:* `domain/rules/` 하위(예: `nutrient_rules.py`, `allergen_rules.py`) 규정 로직으로 분리하거나, DB 가이드라인 테이블(`domain/models/guideline.py`)에서 불러오는 방식으로 변경해야 합니다.

### 🟢 3. LangGraph (오케스트레이션) 고유 코드 (유지 및 모듈화)
LangGraph의 워크플로우를 정의하고 상태를 관리하는 핵심 코드로, `ai/` 디렉토리 하위로 깔끔하게 정리되어야 합니다.

- **State 스키마 정의**
  - `DiseaseInfo`, `overallState` (TypedDict)
  - `KFDAAllergen` (Enum)
  - *이동 위치:* `ai/state/schema.py`
- **Graph 초기화 및 Node/Edge 연결**
  - `workflow = StateGraph(overallState)`
  - `workflow.add_node(...)` 및 `workflow.add_edge(...)`
  - `workflow.add_conditional_edges(...)`
  - `app = workflow.compile()`
  - *이동 위치:* `ai/orchestrator/graph.py`

### 🔵 4. 설명 및 시각화용 코드 (삭제/문서화)
노트북 환경에서 테스트와 확인을 위해 작성되었던 파편화된 주석 및 코드입니다.

- **마크다운 텍스트 파편 및 주석 가이드**
  - `"""# 🤖 에이전트 개요..."""`, `START: 유저가 [장바구니 담기] 버튼을 클릭함` 등의 텍스트
  - *이유:* 프로젝트 위키나 별도의 `docs/` 폴더 내 설명서 리드미로 분리 삭제 요망.
- **실행 및 시각화 스크립트**
  - `generate_final_profile` 실행 예시(`print(json.dumps(...))`)
  - `IPython.display` 기반 그래프 시각화 로직
  - `app.invoke(initial_input)` 등 최하단 테스트 실행부
  - *이유:* `tests/test_orchestrator.py` 같은 테스트 코드로 분리하고, 메인 프로덕션 코드에서는 제거해야 합니다.

---

## 2️⃣ `프로젝트폴더구조.md` 기반 리팩토링(분리) 가이드

위 분석을 바탕으로 기존 코드를 새 구조에 맞게 마이그레이션하는 단계별 가이드입니다.

### 📍 Step 1: State 및 Schema 분리 (`ai/state/schema.py`)
- `overallState` 타입 딕셔너리와 `KFDAAllergen` Enum, `DiseaseInfo`를 `ai/state/schema.py` 로 이동시킵니다.
- **규칙:** 앞으로 모든 에이전트는 이 통합 Schema 하나만 참조(`from ai.state.schema import overallState`)해야 합니다.

### 📍 Step 2: 정책 및 가이드라인 로직 분리 (`domain/rules/`)
- `generate_final_profile` 함수 로직과 내부의 `disease_thresholds` 하드코딩 변수들을 `domain/services/user_service.py` 또는 `domain/rules/nutrient_rules.py` 로 옮깁니다. (DB화 전까지 임시 보관)
- `FOOD_DB_MAPPER`, `allergy_substitution_rules` 역시 `domain/rules/` 하위 파일로 이관합니다.

### 📍 Step 3: 핵심 Workflow 로직의 `graph.py` 화 (`ai/orchestrator/graph.py`)
- `langgrapharchitecture.py`를 삭제하고 새롭게 `ai/orchestrator/graph.py`를 생성합니다.
- 해당 파일에서는 오직 다음 기능만 수행합니다.
  1. `from ai.state.schema import overallState` (State 불러오기)
  2. `from ai.agents import user_agent, chat_core, reco_agent, substitution_agent` (각 실제 에이전트 모듈 불러오기)
  3. `from ai.orchestrator.policy import RouterLogic` (라우터 불러오기)
  4. `workflow.add_node`, `add_edge`, `compile()` 로직만 작성.
- LLM 로드(`Qwen2.5`) 로직이나 `del model`, `torch.cuda.empty_cache()` 같은 노트북 특화 코드는 이 파일에 존재해선 안 됩니다.

### 📍 Step 4: 잔재 코드 정리 (Tests 및 찌꺼기 삭제)
- 시각화(`draw_mermaid_png()`)나 하단 `initial_input = {"user_id": "start_user"}`을 통한 그래프 임의 실행 코드는 `tests/test_orchestrator.py`로 옮겨서 pytest 용도로 전환합니다.
- `Mock DB(products, final_profiles)` 객체는 삭제하거나, 데이터베이스 파이프라인(`scripts/seed_demo_data.py`) 스크립트 작성 시 참고용으로만 빼두고 완전히 폐기합니다.
