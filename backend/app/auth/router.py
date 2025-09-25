"""
인증 시스템 메인 라우터
모든 인증 관련 엔드포인트를 통합 관리
"""

from fastapi import APIRouter
from .NotLogin import register, login, refresh
from .Login import profile, delete

# 메인 인증 라우터 생성
auth_router = APIRouter()

# NotLogin 라우터들 (인증 불필요)
auth_router.include_router(
    register.router,
    tags=["Authentication - Registration"]
)

auth_router.include_router(
    login.router,
    tags=["Authentication - Login"]
)

auth_router.include_router(
    refresh.router,
    tags=["Authentication - Token Management"]
)

# Login 라우터들 (인증 필요)
auth_router.include_router(
    profile.router,
    tags=["Authentication - Profile Management"]
)

auth_router.include_router(
    delete.router,
    tags=["Authentication - Account Management"]
)

# 라우터 정보
@auth_router.get(
    "/auth/info",
    tags=["Authentication - System Info"],
    summary="인증 시스템 정보",
    description="인증 시스템의 기본 정보와 사용 가능한 엔드포인트를 반환합니다."
)
async def get_auth_system_info():
    """인증 시스템 정보 반환"""
    return {
        "system": "JWT Authentication System",
        "version": "1.0.0",
        "features": [
            "회원가입 (Registration)",
            "로그인 (Login)",
            "토큰 갱신 (Token Refresh)",
            "회원정보 수정 (Profile Update)",
            "회원탈퇴 (Account Deletion)"
        ],
        "token_config": {
            "access_token_expire_minutes": 15,
            "refresh_token_expire_days": 1,
            "algorithm": "HS256"
        },
        "endpoints": {
            "no_auth_required": [
                "POST /auth/register - 회원가입",
                "POST /auth/login - 로그인",
                "POST /auth/refresh - 토큰 갱신",
                "POST /auth/logout - 로그아웃",
                "GET /auth/check-email/{email} - 이메일 중복 확인",
                "POST /auth/validate-token - 토큰 검증",
                "GET /auth/login-status - 로그인 상태 확인"
            ],
            "auth_required": [
                "GET /auth/me - 현재 사용자 정보",
                "PUT /auth/profile - 회원정보 수정",
                "DELETE /auth/account - 회원탈퇴",
                "GET /auth/profile/summary - 프로필 요약",
                "POST /auth/account/verify-password - 비밀번호 확인",
                "GET /auth/account/deletion-info - 계정 삭제 안내"
            ]
        }
    }