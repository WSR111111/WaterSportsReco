"""
JWT 인증 미들웨어 및 의존성 주입
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any, Optional
from .jwt_handler import verify_access_token
from .utils import get_user_by_id
import logging

logger = logging.getLogger(__name__)

# HTTP Bearer 토큰 스키마
security = HTTPBearer()

class AuthMiddleware:
    """인증 미들웨어 클래스"""
    
    @staticmethod
    async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> Dict[str, Any]:
        """현재 인증된 사용자 정보 반환"""
        try:
            # 토큰에서 Bearer 제거
            token = credentials.credentials
            
            # 토큰 검증
            token_data = verify_access_token(token)
            
            # 데이터베이스에서 최신 사용자 정보 조회
            user_data = await get_user_by_id(token_data["user_id"])
            if not user_data:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="사용자를 찾을 수 없습니다.",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # 비밀번호 해시 제거
            user_info = {k: v for k, v in user_data.items() if k != 'password_hash'}
            return user_info
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"사용자 인증 오류: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="인증에 실패했습니다.",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    @staticmethod
    async def get_current_user_optional(
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
    ) -> Optional[Dict[str, Any]]:
        """선택적 사용자 인증 (토큰이 없어도 허용)"""
        if not credentials:
            return None
        
        try:
            return await AuthMiddleware.get_current_user(credentials)
        except HTTPException:
            return None
    
    @staticmethod
    async def verify_user_access(
        current_user: Dict[str, Any] = Depends(get_current_user),
        target_user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """사용자 접근 권한 확인 (자신의 정보만 접근 가능)"""
        if target_user_id and current_user["id"] != target_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="다른 사용자의 정보에 접근할 수 없습니다."
            )
        
        return current_user

# 의존성 주입 함수들
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """현재 인증된 사용자 정보 반환 (의존성 주입용)"""
    return await AuthMiddleware.get_current_user(credentials)

async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[Dict[str, Any]]:
    """선택적 사용자 인증 (의존성 주입용)"""
    return await AuthMiddleware.get_current_user_optional(credentials)

async def get_current_active_user(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """활성 사용자 확인 (향후 사용자 상태 관리 시 확장 가능)"""
    # 현재는 단순히 인증된 사용자 반환
    # 향후 사용자 활성/비활성 상태 확인 로직 추가 가능
    return current_user

def require_auth(func):
    """인증 필수 데코레이터"""
    async def wrapper(*args, **kwargs):
        # FastAPI의 Depends를 사용하므로 실제로는 사용하지 않음
        # 문서화 목적으로 유지
        return await func(*args, **kwargs)
    return wrapper

class TokenValidator:
    """토큰 검증 유틸리티 클래스"""
    
    @staticmethod
    def extract_token_from_header(authorization: str) -> str:
        """Authorization 헤더에서 토큰 추출"""
        if not authorization:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization 헤더가 없습니다.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        try:
            scheme, token = authorization.split()
            if scheme.lower() != "bearer":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Bearer 토큰이 아닙니다.",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return token
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="잘못된 Authorization 헤더 형식입니다.",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    @staticmethod
    async def validate_user_permission(
        current_user: Dict[str, Any],
        resource_user_id: int,
        action: str = "access"
    ) -> bool:
        """사용자 권한 검증"""
        if current_user["id"] != resource_user_id:
            logger.warning(
                f"권한 없는 접근 시도: user_id={current_user['id']}, "
                f"target_user_id={resource_user_id}, action={action}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"해당 리소스에 대한 {action} 권한이 없습니다."
            )
        return True

# 에러 응답 생성 함수
def create_auth_error_response(detail: str, status_code: int = status.HTTP_401_UNAUTHORIZED):
    """인증 에러 응답 생성"""
    return HTTPException(
        status_code=status_code,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )