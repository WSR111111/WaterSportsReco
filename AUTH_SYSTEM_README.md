🔑 JWT Refresh Token vs 난수 Refresh Token 차이
1. JWT Refresh Token

구조: 헤더.페이로드.서명 → . 점 2개 포함

안에 exp, iat, sub 같은 정보가 들어있음

장점

자체적으로 만료 시간(exp) 확인 가능 (서버 DB 안 봐도 됨)

무상태(stateless) 관리 가능 → 서버 확장성 유리

단점

클라이언트가 토큰을 탈취하면 만료 전까지는 막을 방법이 없음 (DB에서 강제로 revoke 불가)

토큰 탈취 시 보안 위험 → 보통 짧은 주기로 발급 권장

2. 난수 Refresh Token (지금 쓰고 있는 방식)

구조: 그냥 랜덤한 문자열

서버 DB(또는 Redis)에 저장해두고, 클라이언트가 보내는 값과 비교

장점

서버에서 강제로 무효화 가능 (DB에서 삭제하면 끝)

토큰 탈취 위험 대응이 더 쉬움

단점

항상 DB(또는 캐시)를 조회해야 함 → 상태(stateful) 관리

서버 확장 시 중앙 저장소 필요 (Redis, shared DB 등)

🔍 실제 서비스에서의 선택

JWT Access Token + 난수 Refresh Token
👉 가장 많이 쓰는 패턴이에요.

Access Token은 짧게 (예: 15분)

Refresh Token은 DB에 저장된 난수 문자열 (예: 7일)

장점: 보안 ↑ (탈취되면 서버에서 무효화 가능)

JWT Access Token + JWT Refresh Token
👉 완전히 stateless한 아키텍처에서 선택하기도 함.

장점: 서버 확장성 ↑

단점: 탈취되면 만료까지 무조건 유효

📌 **지금 쓰고 계신 방식(난수 Refresh Token)**은 더 안전한 쪽이에요.
→ 서버에서 Refresh Token을 언제든지 강제로 무효화(revoke)할 수 있고, 탈취 대응이 유리합니다.

✅ 정리

Access Token은 JWT → 유효기간 짧음 (15분)

Refresh Token은 난수 문자열 → 서버 DB에서 관리 (1일)

이 조합이 업계에서도 가장 흔하고 안전한 방식

## 🚀 주요 기능

### 백엔드 (FastAPI)
- ✅ 회원가입 (이메일 중복 확인, 비밀번호 정책)
- ✅ 로그인 (JWT 토큰 발급)
- ✅ 토큰 갱신 (Refresh Token)
- ✅ 회원정보 수정
- ✅ 회원탈퇴
- ✅ 비밀번호 해싱 (bcrypt)
- ✅ 토큰 자동 만료 관리

### 프론트엔드 (React)
- ✅ 회원가입 페이지
- ✅ 로그인 페이지  
- ✅ 회원정보 수정 페이지
- ✅ 회원탈퇴 페이지
- ✅ 인증 컨텍스트 (전역 상태 관리)
- ✅ 라우트 가드 (인증 보호)
- ✅ 자동 토큰 갱신

## 📁 프로젝트 구조

```
backend/app/auth/
├── Login/                  # 인증 필요 기능
│   ├── profile.py         # 회원정보 수정
│   └── delete.py          # 회원탈퇴
├── NotLogin/              # 인증 불필요 기능
│   ├── register.py        # 회원가입
│   ├── login.py           # 로그인
│   └── refresh.py         # 토큰 갱신
├── models.py              # 데이터 모델
├── database.py            # DB 연결
├── jwt_handler.py         # JWT 관리
├── middleware.py          # 인증 미들웨어
├── utils.py               # 유틸리티
└── router.py              # 라우터 통합

frontend/src/
├── components/auth/
│   ├── AuthContext.jsx    # 인증 컨텍스트
│   ├── AuthGuard.jsx      # 라우트 보호
│   └── apiClient.js       # API 클라이언트
├── pages/auth/
│   ├── Register.jsx       # 회원가입
│   ├── Login.jsx          # 로그인
│   ├── Profile.jsx        # 회원정보 수정
│   └── DeleteAccount.jsx  # 회원탈퇴
└── router/
    └── index.js           # 라우터 설정

dbeaver_setting/
└── init_auth.sql          # DB 스키마
```

## 🛠️ 설치 및 설정

### 1. 백엔드 의존성 설치

```bash
cd backend
pip install -r requirements.txt
```

### 2. 환경변수 설정

`.env` 파일에 다음 설정이 포함되어 있는지 확인:

```env
# JWT 설정
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=1
BCRYPT_ROUNDS=12

# MySQL 설정
MYSQL_HOST=localhost
MYSQL_PORT=3307
MYSQL_DATABASE=watersports
MYSQL_USER=wsuser
MYSQL_PASSWORD=wspass
```

### 3. 데이터베이스 초기화

```sql
-- dbeaver_setting/init_auth.sql 실행
mysql -u wsuser -p watersports < dbeaver_setting/init_auth.sql
```

### 4. 프론트엔드 설정

```bash
cd frontend
npm install
```

## 🚀 실행 방법

### 백엔드 서버 실행
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 프론트엔드 서버 실행
```bash
cd frontend
npm run dev
```

## 🧪 테스트

### 백엔드 API 테스트
```bash
cd backend
python test_auth.py
```

### 수동 테스트
1. http://localhost:5173/register - 회원가입
2. http://localhost:5173/login - 로그인
3. http://localhost:5173/profile - 회원정보 수정
4. http://localhost:5173/delete-account - 회원탈퇴

## 📚 API 문서

### 인증 불필요 엔드포인트

#### 회원가입
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "Password123!",
  "name": "사용자"
}
```

#### 로그인
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "Password123!"
}
```

#### 토큰 갱신
```http
POST /api/auth/refresh
Content-Type: application/json

{
  "refresh_token": "your-refresh-token"
}
```

### 인증 필요 엔드포인트

#### 현재 사용자 정보
```http
GET /api/auth/me
Authorization: Bearer your-access-token
```

#### 회원정보 수정
```http
PUT /api/auth/profile
Authorization: Bearer your-access-token
Content-Type: application/json

{
  "name": "새 이름",
  "password": "NewPassword123!",
  "current_password": "CurrentPassword123!"
}
```

#### 회원탈퇴
```http
DELETE /api/auth/account
Authorization: Bearer your-access-token
Content-Type: application/json

{
  "password": "CurrentPassword123!"
}
```

## 🔒 보안 기능

### 비밀번호 정책
- 최소 8자 이상
- 대문자, 소문자, 숫자, 특수문자 포함
- bcrypt 해싱 (rounds: 12)

### JWT 토큰
- Access Token: 15분 만료
- Refresh Token: 1일 만료
- HS256 알고리즘
- 자동 갱신 지원

### 보안 헤더
- CORS 설정
- 입력 검증
- SQL 인젝션 방지

## 🎨 프론트엔드 기능

### 인증 컨텍스트
```jsx
import { useAuth } from './components/auth/AuthContext';

function MyComponent() {
  const { user, isAuthenticated, login, logout } = useAuth();
  
  // 인증 상태에 따른 UI 렌더링
}
```

### 라우트 보호
```jsx
import AuthGuard from './components/auth/AuthGuard';

function ProtectedPage() {
  return (
    <AuthGuard requireAuth={true}>
      <div>인증된 사용자만 볼 수 있는 내용</div>
    </AuthGuard>
  );
}
```

## 🐛 문제 해결

### 일반적인 문제들

1. **토큰 만료 오류**
   - 자동 갱신이 실패한 경우 다시 로그인

2. **CORS 오류**
   - 백엔드 CORS 설정 확인
   - 프론트엔드 API URL 확인

3. **데이터베이스 연결 오류**
   - MySQL 서버 실행 상태 확인
   - 환경변수 설정 확인

4. **비밀번호 정책 오류**
   - 대소문자, 숫자, 특수문자 포함 확인

## 📈 향후 개선 사항

- [ ] OAuth 소셜 로그인 (Google, Kakao)
- [ ] 2단계 인증 (2FA)
- [ ] 이메일 인증
- [ ] 비밀번호 재설정
- [ ] 사용자 역할 관리 (RBAC)
- [ ] 로그인 기록 관리
- [ ] 계정 잠금 기능