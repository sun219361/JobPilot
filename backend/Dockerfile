FROM python:3.12-slim

WORKDIR /app

# 시스템 의존성
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# uv 설치 (pip 대신 빠른 패키지 설치)
RUN pip install uv

# 의존성 파일 복사 및 설치
COPY pyproject.toml .
RUN uv pip install --system -e .

# 소스 복사
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
