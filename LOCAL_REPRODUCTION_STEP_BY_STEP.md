# AI-NutriCurator 로컬 재현 가이드 (Step-by-Step)

이 문서는 **다른 로컬 PC에서 현재 프로젝트를 동일하게 재현**하기 위한 작업을 순서대로 정리한 가이드입니다.

---

## 0) 사전 준비

아래 도구를 먼저 설치합니다.

- Git
- Python `3.11.x`
- Node.js `20.x` (LTS 권장) + npm
- Docker Desktop (Docker 방식으로 실행할 경우)
- PostgreSQL 클라이언트(`psql`) 선택 사항

권장 포트:

- Backend API: `8000`
- Frontend(Next.js): `3001`
- PostgreSQL: `5432`

---

## 1) 저장소 클론

```bash
git clone <YOUR_REPO_URL>
cd AI_NutriCurator
```

---

## 2) 환경변수 파일 생성

루트 경로에 `.env` 파일을 생성하고 아래 값을 넣습니다.

```env
POSTGRES_DB=appdb
POSTGRES_USER=appuser
POSTGRES_PASSWORD=apppassword
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
AI_DATA_SOURCE=postgres
```

선택(권장) 변수:

```env
JWT_SECRET_KEY=dev-secret-change-me
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
```

> 운영 환경에서는 비밀번호/시크릿을 반드시 변경하세요.

---

## 3) 백엔드 + DB 실행 방법 선택

아래 둘 중 하나를 선택합니다.

---

### 방법 A) Docker Compose로 실행 (권장)

1. 루트에서 컨테이너 실행

```bash
docker compose up --build
```

2. 내부 동작
   - `postgres` 컨테이너 기동
   - `api` 컨테이너에서 `alembic upgrade head` 실행 후 `uvicorn app.main:app` 실행

3. 확인
   - API 문서: `http://localhost:8000/docs`

---

### 방법 B) 로컬 Python + 로컬 Postgres로 실행

1. 가상환경 생성/활성화

```bash
python -m venv .venv
```

Windows PowerShell:

```bash
.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

2. 의존성 설치

```bash
pip install -r requirements.txt
```

3. PostgreSQL 실행 후 DB/사용자 준비
   - `.env` 기준으로 DB(`appdb`)와 사용자(`appuser`)가 존재해야 합니다.

4. 마이그레이션 적용

```bash
python -m alembic upgrade head
```

5. API 실행

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

6. 확인
   - API 문서: `http://localhost:8000/docs`

---

## 4) 프론트엔드 실행

1. 프론트 폴더 이동

```bash
cd frontend
```

2. 패키지 설치

```bash
npm install
```

3. (선택) API 프록시 대상 변경이 필요하면 환경변수 지정
   - 기본값은 `http://localhost:8000` 입니다.

Windows PowerShell:

```bash
$env:NEXT_PUBLIC_API_URL="http://localhost:8000"
```

macOS/Linux:

```bash
export NEXT_PUBLIC_API_URL=http://localhost:8000
```

4. 개발 서버 실행

```bash
npm run dev
```

5. 확인
   - 프론트: `http://localhost:3001`

---

## 5) 데이터 재현 (필요 시)

백엔드는 DB 기반이므로, 기존 환경과 **동일한 데이터**가 필요하면 아래를 추가로 수행합니다.

### 5-1) 최소 계정 데이터 추가

루트에서:

```bash
python scripts/run_add_master_user.py
```

### 5-2) 사용자 비밀번호 규칙 적용(옵션)

```bash
python scripts/update_user_passwords.py
```

### 5-3) 상품 데이터 적재(옵션)

`scripts/load_products_from_original_csv.py`는 기본적으로 `products_ver2.csv` 파일을 기대합니다.  
해당 파일이 준비된 경우에만 실행하세요.

```bash
python scripts/load_products_from_original_csv.py
```

> 이 스크립트는 `pandas`, `numpy`가 필요할 수 있습니다. 없다면 설치 후 실행합니다.
>
> ```bash
> pip install pandas numpy
> ```

### 5-4) 데이터 확인(옵션)

```bash
python scripts/query_users_profiles.py
```

---

## 6) 동작 검증 체크리스트

아래 순서대로 체크하면 "동일 재현" 여부를 빠르게 판단할 수 있습니다.

1. `http://localhost:8000/docs` 접속 가능
2. `GET /api/v1/products` 호출 시 200 응답
3. `http://localhost:3001` 접속 가능
4. 프론트에서 회원가입/로그인 동작
5. 상품 목록/상세 조회 동작
6. AI 분석 요청(`/api/v1/ai/analyze`) 동작

---

## 7) 자주 발생하는 이슈

### 1) `Connection refused` (DB 연결 실패)

- `.env`의 `POSTGRES_HOST/PORT/USER/PASSWORD/DB` 확인
- Docker 사용 시 `docker compose ps`로 postgres 상태 확인

### 2) CORS 오류

- 프론트는 `3001`, 백엔드는 `8000` 기준으로 구성됨
- 프론트 실행 포트를 바꿨다면 CORS 설정(`app/main.py`)도 맞춰야 함

### 3) API 컨테이너가 마이그레이션에서 실패

- DB가 비어 있는데 현재 마이그레이션이 기대와 다를 수 있음
- 기존 팀 DB 덤프 또는 동일 스키마 초기화 방법을 공유받아 적용 필요

### 4) 프론트에서 API 호출 실패

- `NEXT_PUBLIC_API_URL`이 실제 백엔드 주소와 일치하는지 확인
- 브라우저 개발자도구 Network 탭에서 `/api/*` 요청 대상 확인

---

## 8) 재현 완료 기준

아래를 모두 만족하면 로컬 재현 완료로 판단합니다.

- 백엔드/DB/프론트가 모두 정상 기동
- 회원가입/로그인/프로필 조회가 동작
- 상품 조회와 AI 분석 API가 정상 응답
- 팀 기준 테스트 데이터(계정/상품)가 필요한 경우 동일하게 적재됨

