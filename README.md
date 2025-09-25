# 프로젝트 구조

## 백엔드 구조 (모듈화된 아키텍처)
```
backend/
├── app/
│   ├── main.py                    # FastAPI 메인 애플리케이션
│   │                              # - CORS 설정
│   │                              # - 데이터 동기화 API 엔드포인트
│   │                              # - 인증 라우터 통합
│   ├── config.py                  # 환경 설정 관리
│   │                              # - API 키 로드 (.env)
│   │                              # - JWT 설정
│   │                              # - CORS 허용 도메인 설정
│   ├── auth/                      # 🔐 인증 시스템 모듈
│   │   ├── models.py              # Pydantic 인증 모델
│   │   ├── dependencies.py        # FastAPI 의존성 주입
│   │   ├── password_service.py    # 비밀번호 해싱/검증
│   │   ├── Login/                 # 로그인 사용자 관련
│   │   │   ├── jwt_service.py     # JWT 토큰 생성/검증
│   │   │   ├── user_service.py    # 사용자 관리 서비스
│   │   │   └── auth_router.py     # 인증 API 엔드포인트
│   │   └── Not_Login/             # 비로그인 사용자 관련
│   │       ├── register_service.py # 회원가입 서비스
│   │       └── public_router.py   # 공개 API 엔드포인트
│   │
│   └── services/                  # 서비스 레이어 (모듈화)
│       ├── clients/               # 외부 API 클라이언트 모듈
│       │   ├── kma/               # 기상청 API 클라이언트
│       │   │   ├── marine_client.py      # 해양 관측소 API 클라이언트
│       │   │   ├── kma_surface_client.py # 지상 관측소 API 클라이언트
│       │   │   └── common.py             # KMA 공통 유틸리티
│       │   └── tourist_client.py         # 한국관광공사 API 클라이언트
│       │
│       ├── db/                    # 데이터베이스 관련 모듈
│       │   ├── manager.py         # DatabaseManager 클래스
│       │   └── repositories/      # Repository 패턴 구현
│       │       ├── region_repository.py   # 지역 데이터 Repository
│       │       ├── sports_repository.py   # 스포츠 카테고리 Repository
│       │       ├── station_repository.py  # 관측소 데이터 Repository
│       │       ├── place_repository.py    # 장소 데이터 Repository
│       │       └── user_repository.py     # 🔐 사용자 데이터 Repository
│       │
│       ├── sync/                  # 동기화 서비스 계층
│       │   ├── sync_marine_service.py     # 해양 데이터 동기화
│       │   ├── sync_surface_service.py    # 지상 데이터 동기화
│       │   ├── sync_leisure_service.py    # 레저 장소 동기화
│       │   ├── sync_category_service.py   # 카테고리 동기화
│       │   ├── sync_region_service.py     # 지역 데이터 동기화
│       │   ├── sync_place_detail_service.py # 장소 상세정보 동기화
│       │   └── sync_ground_station_service.py # 지상 관측소 정보 동기화
│       │
│       └── utils/                 # 유틸리티 함수들
│           ├── json_parser.py     # JSON 파싱 유틸리티
│           └── time_formatter.py  # 시간 형식 변환 유틸리티
│
└── requirements.txt               # Python 의존성 패키지
                                   # - PyJWT, bcrypt, python-multipart 추가
```

### 백엔드 아키텍처 특징
- **모듈화된 구조**: 관심사 분리를 통한 유지보수성 향상
- **Repository 패턴**: 데이터 접근 로직 캡슐화
- **서비스 계층**: 비즈니스 로직과 데이터 접근 분리
- **의존성 주입**: 각 서비스가 필요한 의존성을 주입받는 구조
- **비동기 컨텍스트 매니저**: 리소스 관리 자동화

### 백엔드 주요 기능
- **외부 API 클라이언트**: 기상청(KMA), 한국관광공사 API 연동
- **데이터 동기화**: 해양/지상 관측소, 관광지 데이터 수집 및 저장
- **데이터베이스 관리**: MySQL 연결 및 Repository 패턴을 통한 CRUD 작업
- **에러 처리**: 타임아웃, 네트워크 오류, 파싱 오류 등 체계적 처리
- **비동기 처리**: httpx를 사용한 고성능 비동기 HTTP 요청

### API 엔드포인트

#### 데이터 동기화 API
- `POST /api/sync/marine` - 해양 관측소 데이터 동기화
- `POST /api/sync/surface` - 지상 관측소 데이터 동기화 (관측소 정보 + 관측 데이터)
- `POST /api/sync/ground-stations` - 지상 관측소 정보만 동기화
- `POST /api/sync/leisure-places` - 레저 장소 데이터 동기화
- `POST /api/sync/place-details` - 장소 상세정보 동기화 (API 제한 고려)
- `POST /api/sync/categories` - 카테고리 코드 동기화
- `POST /api/sync/regions` - 지역 데이터 동기화

#### 인증 API
- `POST /auth/register` - 회원가입
- `POST /auth/login` - 로그인
- `POST /auth/logout` - 로그아웃
- `POST /auth/refresh` - 토큰 갱신
- `GET /auth/me` - 사용자 정보 조회
- `PUT /auth/me` - 사용자 정보 수정
- `DELETE /auth/me` - 회원탈퇴
- `POST /auth/change-password` - 비밀번호 변경
- `POST /auth/check-email` - 이메일 중복 확인
- `GET /auth/me/activity` - 사용자 활동 기록 조회
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
│   │   ├── Header.jsx             # 🔐 인증 버튼 포함 헤더
│   │   ├── Footer.jsx             # 푸터 컴포넌트
│   │   ├── auth/                  # 🔐 인증 관련 컴포넌트
│   │   │   ├── LoginForm.jsx      # 로그인 폼
│   │   │   ├── RegisterForm.jsx   # 회원가입 폼
│   │   │   └── AuthModal.jsx      # 인증 모달
│   │   └── pages/                 # 페이지 컴포넌트
│   │       ├── LoginPage.jsx      # 로그인 페이지
│   │       ├── RegisterPage.jsx   # 회원가입 페이지
│   │       └── MyPage.jsx         # 마이페이지
│   ├── router/                    # 🔐 라우팅 관련
│   │   ├── index.js               # React Router 설정
│   │   ├── ProtectedRoute.jsx     # 보호된 라우트
│   │   └── PublicRoute.jsx        # 공개 라우트
│   ├── context/                   # 🔐 상태 관리
│   │   └── AuthContext.jsx        # 인증 컨텍스트
│   ├── hooks/                     # 커스텀 훅
│   │   ├── useKakaoLoader.js      # 카카오맵 API 로드 훅
│   │   ├── useAuth.js             # 🔐 인증 훅
│   │   └── useApi.js              # 🔐 API 호출 훅
│   ├── api/                       # API 클라이언트
│   │   ├── client.js              # 기본 API 클라이언트
│   │   └── auth.js                # 🔐 인증 API 클라이언트
│   ├── App.jsx                    # 메인 앱 컴포넌트
│   ├── AppRouter.jsx              # 🔐 라우터 컴포넌트
│   └── main.jsx                   # 앱 진입점
├── vite.config.js                 # Vite 빌드 설정
└── package.json                   # Node.js 의존성 패키지
                                   # - react-router-dom 추가
```
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

# 개발 환경
- Frontend: React 18, Vite, React Router, 카카오맵 API
- Backend: FastAPI, Python 3.9+, JWT, bcrypt
- Database: MySQL 8.0
- External APIs: 기상청(KMA), 국립해양조사원(KHOA), 한국관광공사