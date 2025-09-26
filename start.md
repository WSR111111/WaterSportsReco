# Docker 실행
cd dbeaver_setting
docker-compose up

# DB 생성 및 연결

# 백엔드
cd backend
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 프론트엔드
cd frontend
npm install
npm run dev

# 연결 테스트
1. 백엔드가 http://localhost:8000 에서 실행 중인지 확인
2. 프론트엔드가 http://localhost:5173 에서 실행 중인지 확인

# 데이터 동기화

1.  backend 실행

2. 브라우저에서 http://localhost:8000/docs
 접속

3. POST API 엔드포인트들을 차례대로 Try it out → Execute 실행
→ 실행할 때마다 DB에 데이터가 저장됨
⚠️ place-details 엔드포인트는 실행 시간이 매우매우 오래걸림 주의
