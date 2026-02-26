# app-postgres 접속 및 현재 스키마 재생성 명령어

## 1) 컨테이너 상태 확인

```powershell
docker compose ps
```

## 2) `app-postgres` 컨테이너 접속

```powershell
docker compose exec postgres bash
```

컨테이너 내부에서 `psql` 바로 접속:

```bash
psql -U appuser -d appdb
```

호스트(로컬)에서 바로 `psql` 실행:

```powershell
docker compose exec -T postgres psql -U appuser -d appdb
```

---

## 3) 현재 DB 스키마 SQL 추출 (schema-only)

컨테이너 내부 `/tmp`에 스키마 SQL 생성:

```powershell
docker compose exec -T postgres pg_dump -U appuser -d appdb --schema-only --no-owner --no-privileges -f /tmp/appdb_schema_only.sql
```

워크스페이스로 복사:

```powershell
docker cp app-postgres:/tmp/appdb_schema_only.sql infra/db/appdb_schema_only.sql
```

---

## 4) 빈 DB에 현재 스키마 만들기 (재생성)

### 4-1. 기존 DB 삭제/생성 (주의: 데이터 삭제됨)

```powershell
docker compose exec -T postgres psql -U appuser -d postgres -c "DROP DATABASE IF EXISTS appdb;"
docker compose exec -T postgres psql -U appuser -d postgres -c "CREATE DATABASE appdb;"
```

### 4-2. 스키마 적용

```powershell
docker compose exec -T postgres psql -U appuser -d appdb -f /tmp/appdb_schema_only.sql
```

> `appdb_schema_only.sql`을 호스트에서 먼저 수정했다면, 다시 컨테이너로 복사 후 적용:
>
> ```powershell
> docker cp infra/db/appdb_schema_only.sql app-postgres:/tmp/appdb_schema_only.sql
> docker compose exec -T postgres psql -U appuser -d appdb -f /tmp/appdb_schema_only.sql
> ```

---

## 5) 스키마 검증 명령어

데이터베이스 목록:

```powershell
docker compose exec -T postgres psql -U appuser -d appdb -c "\l"
```

테이블 목록:

```powershell
docker compose exec -T postgres psql -U appuser -d appdb -c "\dt+ public.*"
```

타입(enum) 목록:

```powershell
docker compose exec -T postgres psql -U appuser -d appdb -c "SELECT typname FROM pg_type WHERE typnamespace = 'public'::regnamespace AND typtype = 'e' ORDER BY typname;"
```

---

## 6) (옵션) 데이터까지 함께 복원하려면

이미 생성한 데이터 덤프(`infra/db/appdb_data_dump.sql`)를 컨테이너에 복사 후 실행:

```powershell
docker cp infra/db/appdb_data_dump.sql app-postgres:/tmp/appdb_data_dump.sql
docker compose exec -T postgres psql -U appuser -d appdb -f /tmp/appdb_data_dump.sql
```

---

## 참고 파일

- 스키마 전용 SQL: `infra/db/appdb_schema_only.sql`
- 데이터 덤프 SQL: `infra/db/appdb_data_dump.sql`
- 원클릭 재생성 스크립트: `infra/db/rebuild_appdb.ps1`

---

## 7) 원클릭 스크립트 사용법 (PowerShell)

스키마만 재생성:

```powershell
powershell -ExecutionPolicy Bypass -File infra/db/rebuild_appdb.ps1
```

스키마 + 데이터까지 복원:

```powershell
powershell -ExecutionPolicy Bypass -File infra/db/rebuild_appdb.ps1 -WithData
```

동작 요약:

1. `postgres` 컨테이너 기동
2. 현재 `appdb` 스키마를 `infra/db/appdb_schema_only.sql`로 추출
3. `appdb` 드롭/재생성
4. 스키마 적용
5. (`-WithData` 시) `infra/db/appdb_data_dump.sql` 적용
6. 최종 테이블 목록 출력
