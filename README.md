
# 환경 설정
## 백엔드 환경변수 (필수)
backend 폴더에 .env 파일 생성:
```
# 기상청 API 키 (해양/지상 관측소 데이터)
KMA_API_KEY=your_kma_api_key_here

# 한국관광공사 API 키 (관광지/레저장소 데이터)
TOURIST_API_KEY=your_tourist_api_key_here

# 카카오 API 키 (지도 서비스)
KAKAO_API_KEY=your_kakao_rest_api_key_here
VITE_KAKAO_APPKEY=your_kakao_javascript_key_here

# CORS 허용 도메인
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# MySQL 데이터베이스 설정
MYSQL_HOST=localhost
MYSQL_DATABASE=watersportsdb
MYSQL_USER=watersports_user
MYSQL_PASSWORD=your_mysql_password_here
MYSQL_PORT=3306
```

## 프론트엔드 환경변수 (필수)
frontend 폴더에 .env 파일 생성:
```
VITE_BACKEND_URL=http://localhost:8000
VITE_KAKAO_APPKEY=your_kakao_api_key_here
```

### 카카오 API 키 발급 방법
1. [Kakao Developers](https://developers.kakao.com/)에 접속
2. 애플리케이션 생성
3. **프론트엔드용**: JavaScript 키 발급 → VITE_KAKAO_APPKEY
4. **백엔드용**: REST API 키 발급 → KAKAO_API_KEY
5. 플랫폼 > Web 플랫폼 등록에서 http://localhost:5173 추가

# 실행 방법
## 백엔드
cd backend
python3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

## 프론트엔드
cd frontend
npm install
npm run dev

# 연결 테스트
1. 백엔드가 http://localhost:8000 에서 실행 중인지 확인
2. 프론트엔드가 http://localhost:5173 에서 실행 중인지 확인
3. 브라우저에서 개발자 도구 > Network 탭에서 API 호출 확인
4. 지도가 로드되고 마커들이 표시되는지 확인
5. 마커 클릭 시 해양 정보가 표시되는지 확인

# 프로젝트 구조

## 백엔드 구조
```
backend/
├── app/
│   ├── main.py                    # FastAPI 메인 애플리케이션
│   │                              # - CORS 설정
│   │                              # - 데이터 동기화 API 엔드포인트
│   ├── config.py                  # 환경 설정 관리
│   │                              # - API 키 로드 (.env)
│   │                              # - CORS 허용 도메인 설정
│   └── services/                  # 서비스 레이어
│       ├── sync_service.py        # 메인 동기화 서비스
│       │                          # - 데이터베이스 연결 관리
│       │                          # - API 데이터 동기화 로직
│       │                          # - 해양/지상 관측소 데이터 처리
│       │                          # - 관광지/레저장소 데이터 처리
│       ├── kma_surface_client.py  # 기상청 지상 관측소 API 클라이언트
│       │                          # - 지상 관측소 정보 조회
│       │                          # - 실시간 기상 데이터 파싱
│       ├── tourist_client.py      # 한국관광공사 API 클라이언트
│       │                          # - 레저 장소 정보 조회 (JSON)
│       │                          # - 장소 상세 정보 조회
│       └── kma/                   # 기상청 해양 관측소 관련
│           ├── __init__.py        # 패키지 초기화
│           ├── common.py          # 공통 유틸리티 함수
│           │                      # - _to_float() 함수
│           │                      # - KMA 예외 클래스들
│           └── marine_client.py   # 기상청 해양 관측소 API 클라이언트
│                                  # - 해양 관측소 정보 조회
│                                  # - 해양 관측 데이터 파싱
└── requirements.txt               # Python 의존성 패키지
```

### 백엔드 주요 기능
- **데이터 동기화 API**: 해양/지상 관측소, 관광지 데이터를 외부 API에서 수집
- **데이터베이스 관리**: MySQL 연결 및 CRUD 작업
- **API 클라이언트**: 기상청(KMA), 한국관광공사 API 연동
- **에러 처리**: 타임아웃, 네트워크 오류, 파싱 오류 등 처리
- **비동기 처리**: httpx를 사용한 비동기 HTTP 요청

### API 엔드포인트
- `POST /api/sync/marine` - 해양 관측소 데이터 동기화
- `POST /api/sync/surface` - 지상 관측소 데이터 동기화  
- `POST /api/sync/leisure-places` - 레저 장소 데이터 동기화
- `POST /api/sync/place-details` - 장소 상세정보 동기화
- `POST /api/sync/categories` - 카테고리 코드 동기화
- `POST /api/sync/regions` - 지역 데이터 동기화
- `POST /api/sync/ground-stations` - 지상 관측소 정보 동기화
## 프론트엔드 구조
```
frontend/
├── public/
│   └── geo/
│       └── korea_sido_simple.json  # 시/도 경계 GeoJSON 데이터
├── src/
│   ├── components/                 # React 컴포넌트
│   │   ├── MapView.jsx            # 카카오맵 지도 컴포넌트
│   │   ├── MarineDataView.jsx     # 해양 데이터 표시 컴포넌트
│   │   ├── ChatWindow.jsx         # AI 챗봇 인터페이스
│   │   ├── RegionFilter.jsx       # 지역 필터링 컴포넌트
│   │   ├── ActivityFilter.jsx     # 활동별 필터링 컴포넌트
│   │   ├── InfoCard.jsx           # 정보 카드 컴포넌트
│   │   ├── Header.jsx             # 헤더 컴포넌트
│   │   └── Footer.jsx             # 푸터 컴포넌트
│   ├── hooks/
│   │   └── useKakaoLoader.js      # 카카오맵 API 로드 훅
│   ├── api/
│   │   └── client.js              # API 클라이언트 설정
│   ├── App.jsx                    # 메인 앱 컴포넌트
│   └── main.jsx                   # 앱 진입점
├── vite.config.js                 # Vite 빌드 설정
└── package.json                   # Node.js 의존성 패키지
## 전체 프로젝트 구조
```
WaterSportsReco/
├── backend/                    # 백엔드 (FastAPI)
├── frontend/                   # 프론트엔드 (React + Vite)
├── database/                   # MySQL 데이터베이스 파일
├── docker-compose.yml          # Docker Compose 설정
├── README.md                   # 프로젝트 문서
├── TROUBLESHOOTING.md          # 문제 해결 가이드
├── 기술설계도.md               # 기술 설계 문서
└── 중간정리.md                 # 프로젝트 중간 정리
```

# 주요 기능
- 🗺️ 카카오맵 기반 인터랙티브 지도
- 🌊 실시간 해양 정보 표시 (수온, 파고, 조류)
- 🏄 지역별 해양레저 사업장 검색 및 표시
- 🎯 활동별 필터링 (스쿠버다이빙, 카약, 요트 등)
- 💬 AI 챗봇 인터페이스
- 📍 시/도 단위 지역 선택 및 애니메이션
- 📍 활동별 색상 구분 마커 표시

# 문제 해결
자세한 문제 해결 가이드는 [TROUBLESHOOTING.md](TROUBLESHOOTING.md)를 참고하세요.

# 개발 환경
- Frontend: React 18, Vite, 카카오맵 API
- Backend: FastAPI, Python 3.9+
- External APIs: 기상청(KMA), 국립해양조사원(KHOA)