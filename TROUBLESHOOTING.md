# 문제 해결 가이드

## 자주 발생하는 문제와 해결 방법

### 1. 지도가 로드되지 않는 경우
- **증상**: 빈 화면 또는 "지도 로딩 중..." 메시지가 계속 표시
- **해결 방법**:
  1. Kakao API 키가 올바르게 설정되어 있는지 확인
  2. 플랫폼 설정에 http://localhost:5173이 등록되어 있는지 확인
  4. 브라우저 콘솔에서 오류 메시지 확인

### 2. 지역 선택 시 지도가 깨지는 경우
- **증상**: 지역 선택 시 지도가 하얗게 변하거나 제대로 표시되지 않음
- **해결 방법**:
  1. 브라우저 새로고침 (F5 또는 Ctrl+R)
  2. 브라우저 캐시 삭제 (Ctrl+Shift+Delete)
  3. 개발자 도구 > Console에서 JavaScript 오류 확인

### 3. API 호출 오류 (CORS)
- **증상**: "CORS policy" 오류 메시지
- **해결 방법**:
  1. 백엔드가 실행 중인지 확인
  2. backend/.env에 ALLOWED_ORIGINS 설정 확인
  3. 프론트엔드 URL이 백엔드 CORS 설정에 포함되어 있는지 확인
  4. 백엔드 재시작: Ctrl+C 후 다시 실행

### 4. 해양 데이터가 표시되지 않는 경우
- **증상**: 마커 클릭 시 데이터가 "-"로 표시
- **해결 방법**:
  1. backend/.env에 KMA_API_KEY가 설정되어 있는지 확인
  2. API 키가 유효한지 확인
  3. 네트워크 연결 상태 확인
  4. 백엔드 로그에서 API 호출 오류 확인

### 5. 포트 충돌 문제
- **증상**: "Port already in use" 오류
- **해결 방법**:
  1. 기존 프로세스 종료:
     - Windows: `netstat -ano | findstr :8000` 후 `taskkill /PID <PID> /F`
     - Mac/Linux: `lsof -i :8000` 후 `kill -9 <PID>`
  2. 다른 포트 사용:
     - 백엔드: `uvicorn app.main:app --port 8001`
     - 프론트엔드: vite.config.js에서 port 변경

### 6. 가상환경 관련 문제
- **증상**: 패키지 import 오류
- **해결 방법**:
  1. 가상환경이 활성화되어 있는지 확인
  2. Windows: `.\.venv\Scripts\Activate.ps1`
  3. Mac/Linux: `source .venv/bin/activate`
  4. 패키지 재설치: `pip install -r requirements.txt`

### 7. Node.js 패키지 문제
- **증상**: 프론트엔드 빌드/실행 오류
- **해결 방법**:
  1. node_modules 삭제: `rm -rf node_modules`
  2. package-lock.json 삭제
  3. 패키지 재설치: `npm install`

## 디버깅 팁

### 브라우저 개발자 도구 활용
1. **Console 탭**: JavaScript 오류 확인
2. **Network 탭**: API 호출 상태 확인
3. **Application 탭**: 로컬 스토리지, 쿠키 확인

### 로그 확인
1. **백엔드 로그**: 터미널에서 API 호출 로그 확인
2. **프론트엔드 로그**: console.log로 상태 확인

### 환경변수 확인
```bash
# 백엔드
cd backend
python -c "from app.config import *; print(f'KMA_API_KEY: {KMA_API_KEY[:10]}...')"

# 프론트엔드
cd frontend
npm run dev -- --debug
```

## 추가 도움말
문제가 계속되면 다음 정보와 함께 이슈를 제기해주세요:
1. 오류 메시지 전체
2. 브라우저 콘솔 스크린샷
3. 실행 환경 (OS, Node.js 버전, Python 버전)
4. 재현 단계
