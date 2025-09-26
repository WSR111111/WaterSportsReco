"""
토큰 갱신 API 엔드포인트 (인증 불필요)
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import ValidationError
from ..models import TokenRefresh, ErrorResponse
from ..jwt_handler import refresh_access_token
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication - No Login Required"])

@router.post(
    "/refresh",
    summary="액세스 토큰 갱신",
    description="리프레시 토큰을 사용하여 새로운 액세스 토큰을 발급합니다.",
    responses={
        200: {
            "description": "토큰 갱신 성공",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer",
                        "expires_in": 900
                    }
                }
            }
        },
        400: {
            "description": "잘못된 요청 데이터",
            "model": ErrorResponse
        },
        401: {
            "description": "유효하지 않은 리프레시 토큰",
            "model": ErrorResponse
        },
        422: {
            "description": "데이터 검증 실패",
            "model": ErrorResponse
        },
        500: {
            "description": "서버 내부 오류",
            "model": ErrorResponse
        }
    }
)
async def refresh_token(token_data: TokenRefresh):
    """
    리프레시 토큰을 사용하여 새로운 액세스 토큰을 발급합니다.
    
    - **refresh_token**: 유효한 리프레시 토큰
    
    성공 시 새로운 15분 유효한 액세스 토큰을 반환합니다.
    기존 리프레시 토큰은 그대로 유지됩니다.
    """
    try:
        # 새 액세스 토큰 발급
        new_token_data = await refresh_access_token(token_data.refresh_token)
        
        logger.info("액세스 토큰 갱신 성공")
        
        return {
            "access_token": new_token_data["access_token"],
            "token_type": new_token_data["token_type"],
            "expires_in": new_token_data["expires_in"]
        }
        
    except HTTPException:
        raise
    except ValidationError as e:
        logger.error(f"토큰 갱신 데이터 검증 오류: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "입력 데이터가 올바르지 않습니다.",
                    "details": {
                        "validation_errors": e.errors()
                    }
                }
            }
        )
    except Exception as e:
        logger.error(f"토큰 갱신 서버 오류: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "토큰 갱신 중 서버 오류가 발생했습니다.",
                    "details": {}
                }
            }
        )

@router.post(
    "/validate-token",
    summary="토큰 유효성 검증",
    description="액세스 토큰의 유효성을 검증합니다.",
    responses={
        200: {
            "description": "토큰 검증 결과",
            "content": {
                "application/json": {
                    "example": {
                        "valid": True,
                        "expires_at": "2024-01-01T12:00:00Z",
                        "time_until_expiry": 850
                    }
                }
            }
        },
        400: {
            "description": "잘못된 요청",
            "model": ErrorResponse
        }
    }
)
async def validate_token(access_token: str):
    """
    액세스 토큰의 유효성을 검증합니다.
    
    - **access_token**: 검증할 액세스 토큰
    
    토큰의 유효성, 만료 시간, 남은 시간 등의 정보를 반환합니다.
    """
    try:
        from ..jwt_handler import JWTHandler, verify_access_token
        
        # 토큰 만료 정보 조회 (검증 없이)
        token_info = JWTHandler.get_token_expiry_info(access_token)
        
        if "error" in token_info:
            return {
                "valid": False,
                "error": token_info["error"]
            }
        
        # 토큰 검증 시도
        try:
            verify_access_token(access_token)
            is_valid = True
        except HTTPException:
            is_valid = False
        
        return {
            "valid": is_valid,
            "expires_at": token_info.get("expires_at"),
            "issued_at": token_info.get("issued_at"),
            "is_expired": token_info.get("is_expired", False),
            "time_until_expiry": token_info.get("time_until_expiry", 0)
        }
        
    except Exception as e:
        logger.error(f"토큰 검증 오류: {e}")
        return {
            "valid": False,
            "error": "토큰 검증 중 오류가 발생했습니다."
        }