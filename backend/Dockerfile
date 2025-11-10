# 임시 Dockerfile

# 1. 베이스 이미지 선택
FROM python:3.11-slim

# 2. 컨테이너 내 작업 디렉토리 설정
WORKDIR /app

# 3. 필요한 파일 복사
COPY requirements.txt .

# 4. 의존성 설치
RUN pip install --no-cache-dir -r requirements.txt

# 5. 소스 복사
COPY ./app ./app

# 6. FastAPI 서버 실행 (uvicorn)
CMD [ "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000" ]