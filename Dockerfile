FROM python:3.11-slim

WORKDIR /app

# psycopg2-binary 쓰면 보통 빌드 도구 없어도 되는데,
# 혹시 모를 의존성 대비해서 최소만 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# ✅ 컨테이너 시작 시: 마이그레이션 적용 -> 서버 실행
CMD ["bash", "-lc", "python -m alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]