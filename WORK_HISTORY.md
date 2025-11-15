# 작업내용
## 1. postgreSQL로 변경 (vectordb 아직 미완성)
## 2. 데이터 csv로 저장하여 db에 저장하는 로직 
## 3. 아직 tourAPI 쓸 수 없는 이슈로 csv로 저장된 데이터를 활용 (동기화 잠시 작동 중지)
# 추가 해야될 작업 내용
## 4. 관측소는 잘 보이는데 관측소에 대한 관측값이 있는것도 있고 없는것도 있음 확인해볼게요...
## 5. place_details도 TourAPI 이슈로 아직 작동 X

### **데이터베이스 실행 (PostgreSQL)**
```bash
# Docker로 PostgreSQL 실행
cd dbeaver_setting
docker-compose up -d

# 확인: PostgreSQL 컨테이너가 실행 중인지 체크
docker ps
```

### **CSV 파일 DB에 INSERT하는 방법**
```bash
# http://localhost:8000/docs에서 다음 API 실행:

📂 CSV Management 섹션에서:
1. POST /api/csv/restore/{data_type}  # CSV 데이터를 DB에 복원

# 지원되는 data_type (순서대로 실행 권장):
- code                 # 코드 테이블
- leisure_places       # 레저 장소 기본 정보  
- observation_station  # 관측소 정보
- observation_data     # 관측 데이터
```

> **💡 실행 순서**: code → leisure_places → observation_station → observation_data  
> **⚠️ 주의**: place_details는 아직 미완성 상태


### 5️⃣ **데이터 동기화 (실제 API 엔드포인트)**
```bash
# 브라우저에서 http://localhost:8000/docs 접속
# 다음 API들을 순서대로 실행:

📍 Region (지역 데이터)
1. POST /api/region/sync   
> TourAPI 복원 후 우리 데이터 구조에 맞게 고쳐야 함 아직 작동 X  

🏟️ Station (관측소 정보)  
2. POST /api/station/sync/all        # 모든 관측소 -> 이거만 실행하면 지상관측소, 해양관측소 둘 다 들어감
3. POST /api/station/sync/surface    # 지상 관측소만 
4. POST /api/station/sync/buoy       # 해양 관측소만  
> all 하나만 실행

🌊 Observation (관측 데이터)
5. POST /api/observation/sync/all    # 모든 관측 데이터 > 이거만 실행하면 지상관측 데이터값, 해양관측 데이터값 둘 다 들어감
6. POST /api/observation/sync/surface # 지상 관측 데이터만  
7. POST /api/observation/sync/buoy   # 해양 관측 데이터만  
> all 하나만 실행

🏃 Sports (스포츠 카테고리)
8. POST /api/sports/sync  
> TourAPI 복원 후 우리 데이터 구조에 맞게 고쳐야 함 아직 작동 X 

🏖️ Leisure (레저 장소) 
9. POST /api/leisure/sync/places     # 레저 장소 기본 정보
10. POST /api/leisure/sync/details   # 레저 장소 상세 정보   
> TourAPI 복원 후 우리 데이터 구조에 맞게 고쳐야 함 아직 작동 X 
```

> **⚠️ 주의사항**: 
> - 관측소 및 관측 데이터는 현재 정상 작동 중
> - 레저 장소 API는 tourAPI 이슈로 일시 중단 상태


## 📁 프로젝트 구조 한눈에 보기

### 🏗️ 전체 프로젝트 구조
```
WaterSportsReco/
├── 📁 backend/                     # FastAPI 백엔드 서버
├── 📁 frontend/                    # React + Vite 프론트엔드
├── 📁 dbeaver_setting/             # PostgreSQL 데이터베이스 설정
├── 📄 .env                         # 환경변수 설정 파일
├── 📄 .gitignore                   # Git 무시 파일 목록
├── 📄 README.md                    # 프로젝트 전체 문서
├── 📄 AUTH_SYSTEM_README.md        # 인증 시스템 상세 문서
├── 📄 start.md                     # 프로젝트 실행 가이드
└── 📄 WORK_HISTORY.md              # 작업 내역 정리 (현재 파일)
```

### 🔧 백엔드 구조 (backend/)
```
backend/
├── 📁 .venv/                       # Python 가상환경
├── 📁 app/                         # 메인 애플리케이션 코드
│   ├── 📄 main.py                  # FastAPI 앱 진입점, 라우터 등록, CORS 설정
│   ├── 📄 config.py                # 환경변수 로드, API 키 관리, DB 설정
│   ├── 📄 database.py              # PostgreSQL 연결 관리, 비동기 DB 세션
│   │
│   ├── 📁 api/                     # REST API 엔드포인트 모음 - 외부 api 불러온걸 db 구조에 맞게 변경 및 동기화 api
│   │   ├── 📄 __init__.py          # API 패키지 초기화
│   │   ├── 📄 routes_region.py     # 지역 데이터 동기화 API
│   │   ├── 📄 routes_station.py    # 관측소 정보 동기화 API
│   │   ├── 📄 routes_observation.py # 관측 데이터 동기화 API
│   │   ├── 📄 routes_sports.py     # 스포츠 카테고리 동기화 API
│   │   ├── 📄 routes_leisure.py    # 레저 장소 동기화 API
│   │   ├── 📄 routes_csv.py        # CSV 파일 관리 API -> csv 파일 DB에 삽입
│   │   └── 📄 routes_data.py       # 실제 DB 데이터 조회 API
│   │
│   ├── 📁 auth/                    # 🔐 JWT 인증 시스템
│   │   ├── 📄 __init__.py          # 인증 패키지 초기화
│   │   ├── 📄 models.py            # Pydantic 인증 모델 (회원가입, 로그인 등)
│   │   ├── 📄 router.py            # 인증 라우터 통합 관리
│   │   ├── 📄 jwt_handler.py       # JWT 토큰 생성/검증 로직
│   │   ├── 📄 middleware.py        # 인증 미들웨어, 토큰 검증
│   │   ├── 📄 utils.py             # 비밀번호 해싱, 유틸리티 함수
│   │   ├── 📁 Login/               # 로그인 사용자 전용 기능
│   │   └── 📁 NotLogin/            # 비로그인 사용자 기능 (회원가입, 로그인)
│   │
│   ├── 📁 services/                # 비즈니스 로직 서비스 계층
│   │   ├── 📄 csv_manager.py       # CSV 파일 저장/관리 클래스 
│   │   ├── 📄 csv_utils.py         # CSV 유틸리티 함수들
│   │   ├── 📄 sync_code.py         # 코드 테이블 동기화 서비스
│   │   ├── 📄 sync_leisure.py      # 레저 장소 데이터 동기화
│   │   ├── 📄 sync_observation_data.py # 관측 데이터 동기화
│   │   ├── 📄 sync_observation_station.py # 관측소 정보 동기화
│   │   ├── 📄 sync_observation.py  # 통합 관측 데이터 동기화
│   │   ├── 📄 sync_region.py       # 지역 데이터 동기화
│   │   ├── 📄 sync_sports.py       # 스포츠 카테고리 동기화
│   │   └── 📄 sync_station.py      # 관측소 동기화
│   │
│   └── 📁 utils/                   # 유틸리티 모듈
│       ├── 📄 api_client.py        # 범용 API 클라이언트
│       ├── 📄 kma_client.py        # 기상청 API 전용 클라이언트
│       └── 📄 tourapi_client.py    # 한국관광공사 API 클라이언트
│
├── 📁 data/                        # CSV 백업 데이터 저장소
│   ├── 📄 code_*.csv               # 코드 테이블 백업
│   ├── 📄 leisure_places_*.csv     # 레저 장소 데이터 백업
│   ├── 📄 observation_data_*.csv   # 관측 데이터 백업
│   ├── 📄 observation_station_*.csv # 관측소 정보 백업
│   └── 📄 place_details_*.csv      # 장소 상세정보 백업
│
├── 📄 requirements.txt             # Python 패키지 의존성 목록
├── 📄 test_auth.py                 # 인증 시스템 테스트 스크립트
├── 📄 test_csv_flow.py             # CSV 플로우 테스트 스크립트
└── 📄 expTest.py                   # 실험용 테스트 파일
```

### 🎨 프론트엔드 구조 (frontend/)
```
frontend/
├── 📁 node_modules/                # npm 패키지 설치 디렉토리
├── 📁 public/                      # 정적 파일
│   └── 📁 geo/
│       └── 📄 korea_sido_simple.json # 한국 시도 경계 GeoJSON 데이터
│
├── 📁 src/                         # 소스 코드
│   ├── 📄 main.jsx                 # React 앱 진입점
│   ├── 📄 App.jsx                  # 메인 앱 컴포넌트
│   │
│   ├── 📁 api/                     # API 통신 모듈
│   │   ├── 📄 client.js            # 기본 axios API 클라이언트
│   │   └── 📄 data.js              # 실제 DB 데이터 조회 API
│   │
│   ├── 📁 components/              # React 컴포넌트
│   │   ├── 📄 MapView.jsx          # 카카오맵 지도 메인 컴포넌트
│   │   ├── 📄 Header.jsx           # 상단 헤더 (인증 버튼 포함)
│   │   ├── 📄 Footer.jsx           # 하단 푸터
│   │   ├── 📄 ActivityFilter.jsx   # 활동별 필터링 컴포넌트
│   │   ├── 📄 ChatWindow.jsx       # AI 챗봇 인터페이스
│   │   ├── 📄 MarineStationMarkers.jsx # 해양 관측소 마커
│   │   ├── 📄 PlaceMarkers.jsx     # 레저 장소 마커
│   │   ├── 📄 SurfaceStationMarkers.jsx # 지상 관측소 마커
│   │   └── 📁 auth/                # 🔐 인증 관련 컴포넌트
│   │
│   ├── 📁 hooks/                   # 커스텀 React 훅
│   │   ├── 📄 useKakaoLoader.js    # 카카오맵 API 로드 훅
│   │   ├── 📄 useData.js           # 실제 DB 데이터 사용 훅
│   │   └── 📄 useMapNavigation.js  # 지도 네비게이션 훅
│   │
│   ├── 📁 pages/                   # 페이지 컴포넌트
│   │   ├── 📄 MainPage.jsx         # 메인 페이지
│   │   ├── 📄 PlaceDetail.jsx      # 장소 상세 페이지
│   │   └── 📁 auth/                # 🔐 인증 관련 페이지
│   │
│   ├── 📁 router/                  # 라우팅 설정
│   │   ├── 📄 index.js             # 메인 라우터 설정
│   │   ├── 📄 index_main.js        # 메인 페이지 라우터
│   │   └── 📄 index_PD.js          # 상세 페이지 라우터
│   │
│   └── 📁 utils/                   # 유틸리티 함수
│       ├── 📄 markerUtils.js       # 지도 마커 유틸리티
│       └── 📄 regionUtils.js       # 지역 데이터 유틸리티
│
├── 📄 index.html                   # HTML 템플릿
├── 📄 package.json                 # npm 패키지 설정
├── 📄 package-lock.json            # npm 의존성 잠금 파일
└── 📄 vite.config.js               # Vite 빌드 도구 설정
```

### 🗄️ 데이터베이스 구조 (dbeaver_setting/)
```
dbeaver_setting/
├── 📁 database/                    # PostgreSQL 데이터 영속화 디렉토리
│   ├── 📁 base/                    # PostgreSQL 시스템 데이터베이스
│   ├── 📁 global/                  # 글로벌 설정 데이터
│   ├── 📁 pg_*/                    # PostgreSQL 내부 디렉토리들
│   ├── 📄 postgresql.conf          # PostgreSQL 메인 설정 파일
│   ├── 📄 pg_hba.conf              # 클라이언트 인증 설정
│   └── 📄 PG_VERSION               # PostgreSQL 버전 정보
│
├── 📄 docker-compose.yml           # PostgreSQL Docker 컨테이너 설정
├── 📄 init.sql                     # 메인 데이터베이스 스키마 초기화
└── 📄 init_auth.sql                # 인증 시스템 테이블 초기화
```
