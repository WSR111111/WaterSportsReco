"""
로그인 API 엔드포인트 (인증 불필요)
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import ValidationError
from ..models import UserLogin, TokenResponse, ErrorResponse
from ..utils import authenticate_user
from ..jwt_handler import create_token_pair
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication - No Login Required"])

@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="로그인",
    description="사용자 인증 후 JWT 토큰을 발급합니다.",
    responses={
        200: {
            "description": "로그인 성공",
            "model": TokenResponse
        },
        400: {
            "description": "잘못된 요청 데이터",
            "model": ErrorResponse
        },
        401: {
            "description": "인증 실패",
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
async def login_user(login_data: UserLogin):
    """
    사용자 로그인을 처리합니다.
    
    - **email**: 등록된 이메일 주소
    - **password**: 계정 비밀번호
    
    성공 시 15분 유효한 Access Token과 1일 유효한 Refresh Token을 반환합니다.
    """
    try:
        # 사용자 인증
        user_data = await authenticate_user(login_data.email, login_data.password)
        
        if not user_data:
            logger.warning(f"로그인 실패 - 잘못된 인증 정보: {login_data.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": {
                        "code": "AUTHENTICATION_FAILED",
                        "message": "이메일 또는 비밀번호가 올바르지 않습니다.",
                        "details": {
                            "field": "credentials",
                            "issue": "인증 정보를 확인해주세요."
                        }
                    }
                }
            )
        
        # JWT 토큰 쌍 생성
        token_data = await create_token_pair(user_data)
        
        logger.info(f"로그인 성공: user_id={user_data['id']}, email={user_data['email']}")
        
        return TokenResponse(
            access_token=token_data["access_token"],
            refresh_token=token_data["refresh_token"],
            token_type=token_data["token_type"],
            expires_in=token_data["expires_in"]
        )
        
    except HTTPException:
        raise
    except ValidationError as e:
        logger.error(f"로그인 데이터 검증 오류: {e}")
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
        logger.error(f"로그인 서버 오류: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "서버 내부 오류가 발생했습니다.",
                    "details": {}
                }
            }
        )

@router.post(
    "/logout",
    summary="로그아웃",
    description="현재 세션을 종료하고 리프레시 토큰을 무효화합니다.",
    responses={
        200: {
            "description": "로그아웃 성공",
            "content": {
                "application/json": {
                    "example": {
                        "message": "로그아웃이 완료되었습니다."
                    }
                }
            }
        },
        400: {
            "description": "잘못된 요청",
            "model": ErrorResponse
        },
        500: {
            "description": "서버 내부 오류",
            "model": ErrorResponse
        }
    }
)
async def logout_user(refresh_token: str):
    """
    사용자 로그아웃을 처리합니다.
    
    - **refresh_token**: 무효화할 리프레시 토큰
    
    리프레시 토큰을 데이터베이스에서 삭제하여 무효화합니다.
    """
    try:
        from ..jwt_handler import JWTHandler
        
        # 리프레시 토큰 무효화
        success = await JWTHandler.revoke_refresh_token(refresh_token)
        
        if success:
            logger.info("로그아웃 성공 - 리프레시 토큰 무효화 완료")
            return {
                "message": "로그아웃이 완료되었습니다."
            }
        else:
            logger.warning("로그아웃 - 유효하지 않은 리프레시 토큰")
            return {
                "message": "로그아웃이 완료되었습니다."  # 보안상 동일한 메시지 반환
            }
        
    except Exception as e:
        logger.error(f"로그아웃 오류: {e}")
        # 로그아웃은 실패해도 클라이언트에서 토큰을 삭제하면 되므로 성공으로 처리
        return {
            "message": "로그아웃이 완료되었습니다."
        }

@router.get(
    "/login-status",
    summary="로그인 상태 확인",
    description="현재 로그인 상태를 확인합니다. (토큰 없이 호출 가능)",
    responses={
        200: {
            "description": "상태 확인 결과",
            "content": {
                "application/json": {
                    "example": {
                        "logged_in": False,
                        "message": "로그인이 필요합니다."
                    }
                }
            }
        }
    }
)
async def check_login_status():
    """
    로그인 상태를 확인합니다.
    
    이 엔드포인트는 인증 없이 호출 가능하며,
    클라이언트에서 토큰 유무를 확인하는 용도로 사용됩니다.
    """
    return {
        "logged_in": False,
        "message": "로그인이 필요합니다.",
        "login_url": "/auth/login"
    }