# PostgreSQL 연동 구조 정리안

## 목표

- AI 분석 파이프라인이 `FAKE_DB` 직접 참조 없이 동작하도록 정리
- `AI_DATA_SOURCE=fake|postgres` 분기와 무관하게 동일한 그래프 실행 경로 유지
- `reco_agent`/`sub_reco_agent`의 상품 조회를 실제 `product_id` 기준으로 통일

## 현재 문제

- `api/routes/ai.py`는 `product_service`를 통해 소스 분기(Fake/Postgres)를 타지만,
  `ai/orchestrator/graph.py`는 `load_fake_db()`를 직접 호출해 에이전트를 초기화함
- 결과적으로 라우터의 상품 조회 기준과 그래프 내부 추천 기준이 달라질 수 있음
- `sub_reco_agent`는 `products_db.get(str(product_id))`만 사용해, key가 인덱스(`"0"`, `"1"`)인 Fake 구조에서 점수가 0으로 고정될 수 있음

## 정리 원칙

- 데이터 접근은 라우터/서비스 계층에서만 결정
- 오케스트레이터 그래프는 외부에서 주입받은 데이터(`products_db`)만 사용
- 에이전트는 key 구조와 무관하게 `product_id` 필드로 조회 가능한 fallback 제공

## 변경 설계

1. `ProductService`에 `get_products_index()` 추가
   - 내부 repo의 `get_products_index()`를 호출하여 분석용 상품 맵을 반환

2. Repo 계층에 `get_products_index()` 추가
   - `FakeProductRepository`: 기존 product dict를 `product_id` key 기반으로 정규화
   - `ProductRepository(Postgres)`: `products` 전체를 읽어 분석용 detail dict 맵으로 반환

3. `graph.py`를 의존성 주입 방식으로 변경
   - `compile_graph(products_db=..., final_profiles=...)` 시그니처로 변경
   - 내부 `load_fake_db()` 제거
   - 에이전트 인스턴스는 `create_workflow(...)` 호출 시점에 생성

4. `api/routes/ai.py`에서 그래프 컴파일 시 주입
   - `products_db = product_service.get_products_index()`
   - `app = compile_graph(products_db=products_db, final_profiles={})`

5. `sub_reco_agent` 상품 조회 보강
   - `get_product_nutrients()`에서 `_resolve_product()` 사용
   - Fake/Postgres key 구조 차이와 무관하게 동일 동작

## 기대 효과

- Fake/Postgres 모드 간 분석 로직 일관성 확보
- `sub_reco_agent` 점수 계산에서 0점 고정 문제 해소
- 향후 DB/캐시/외부 검색으로 데이터 소스가 바뀌어도 그래프는 동일 인터페이스 유지

## 검증 체크리스트

- `AI_DATA_SOURCE=fake`:
  - `/api/v1/ai/analyze` 응답의 `full_state_debug.candidates` 존재
  - `full_state_debug.sub_recommendations.score`가 모두 0이 아닌 값 포함

- `AI_DATA_SOURCE=postgres`:
  - `get_products_index()`가 DB row를 반환하고 그래프가 해당 데이터로 동작
  - analyze 응답의 `alternatives`가 DB 상세와 일관된 상품명/이미지 매핑
