# 임시 Dockerfile

# 1. Node.js 베이스 이미지
FROM node:20-alpine

# 2. 작업 디렉토리
WORKDIR /app

# 3. package.json 복사 후 설치
COPY package*.json ./
RUN npm install

# 4. 나머지 파일 복사

COPY . .

# 5. 개발 서버 실행 (Vite)
CMD [ "npm", "run", "dev" ]