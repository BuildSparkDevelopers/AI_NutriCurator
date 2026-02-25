# 다른 로컬에서 작업 이어가기 가이드 (`test/fakedb`)

## 핵심 개념
같은 브랜치를 받아도 실행 결과는 **`.env` + DB 스키마(마이그레이션) + DB 데이터 + 실행 방식(로컬/도커)**가 같아야 동일합니다.

---

## 1) 코드 동기화

```powershell
git fetch origin
git switch test/fakedb
git pull origin test/fakedb
git log --oneline -n 5
```

- 최근 로그에 `d3019fe`가 보이면 이번 작업분까지 정상 반영 상태입니다.

---

## 2) `.env` 동기화 (가장 중요)

`app/settings.py`는 `.env`를 읽어 DB URL을 조합합니다.  
다른 PC에서도 최소 아래 키가 동일해야 합니다.

- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_HOST`
- `POSTGRES_PORT`
- `AI_DATA_SOURCE`

### 주의 포인트

- `AI_DATA_SOURCE`
  - `fake`: FakeDB 플로우
  - `postgres`: 실제 Postgres 플로우
- `POSTGRES_HOST`
  - 앱을 **로컬에서 실행**: 보통 `localhost`
  - 앱을 **도커 api 컨테이너에서 실행**: `postgres`  
    (`docker-compose.yml`에 `api` 서비스 환경변수로 이미 설정됨)

---

## 3) DB 컨테이너/상태 맞추기

### A. 기존 데이터 유지

```powershell
docker compose up -d postgres
docker compose ps
```

### B. 완전 초기화 후 재현

```powershell
docker compose down -v
docker compose up -d postgres
```

- `-v`는 볼륨까지 삭제하므로 DB 데이터가 초기화됩니다.
- 팀 내 동일 재현 목적이면 초기화 방식이 가장 깔끔합니다.

---

## 4) 마이그레이션 동기화

이번 변경에는 Alembic migration이 포함되어 있으므로 다른 로컬 DB에도 반드시 적용해야 합니다.

```powershell
# (가상환경 활성화 후)
alembic current
alembic upgrade head
alembic current
```

- 첫 `current`: 현재 revision 확인
- `upgrade head`: 최신 스키마 반영
- 마지막 `current`: 최신 head 도달 확인

---

## 5) 데이터 시드/보조 스크립트 동기화 (필요 시)

테스트 기준을 맞추려면 같은 순서로 실행하는 것을 권장합니다.

- `scripts/load_products_from_original_csv.py`
- `scripts/run_add_master_user.py`
- `scripts/update_master_activity.py`
- `scripts/update_test_profiles_11_14.py`
- `scripts/update_user_passwords.py`
- `scripts/query_users_profiles.py`

---

## 6) 실행 방식별 체크

### 로컬 Python 실행

```powershell
# venv 활성화 후
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker로 API까지 실행

```powershell
docker compose up -d
docker compose ps
```

- `Dockerfile`에서 컨테이너 시작 시 `alembic upgrade head`를 수행하도록 구성되어 있습니다.

---

## 7) 최종 검증

```powershell
.\run_test.ps1
```

이 스크립트는 다음을 확인합니다.

- `AI_DATA_SOURCE` 값
- `/api/v1/ai/analyze` 호출 결과
- 핵심 응답 필드(candidates/sub_recommendations/final_answer) 상태

---

## 자주 발생하는 이슈

- `.env` 키는 있는데 `AI_DATA_SOURCE` 값이 다름
- 로컬 실행인데 `POSTGRES_HOST=postgres`로 둠 (또는 반대)
- migration 파일만 받고 `alembic upgrade head`를 안 함
- 도커 볼륨이 남아 구버전 데이터가 섞임
- 브랜치가 `test/fakedb`가 아님

---

## 빠른 점검 체크리스트

- [ ] `test/fakedb` 최신 pull 완료
- [ ] `.env` 핵심 키 6개 확인
- [ ] Postgres 정상 기동 (`docker compose ps`)
- [ ] `alembic upgrade head` 완료
- [ ] 필요 시 시드 스크립트 실행
- [ ] `.\run_test.ps1` 통과
