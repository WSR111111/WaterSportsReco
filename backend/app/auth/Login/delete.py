"""
회원탈퇴 API 엔드포인트 (인증 필요)
"""

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import ValidationError
from typing import Dict, Any
from ..models import UserDelete, SuccessResponse, ErrorResponse
from ..middleware import get_current_user
from ..utils import delete_user, verify_password, get_user_by_id, delete_user_refresh_tokens
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication - Login Required"])

@router.delete(
    "/account",
    response_model=SuccessResponse,
    summary="회원탈퇴",
    description="인증된 사용자의 계정을 삭제합니다.",
    responses={
        200: {
            "description": "회원탈퇴 성공",
            "model": SuccessResponse
        },
        400: {
            "description": "잘못된 요청 데이터",
            "model": ErrorResponse
        },
        401: {
            "description": "인증 실패",
            "model": ErrorResponse
        },
        403: {
            "description": "비밀번호 불일치",
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
async def delete_account(
    delete_data: UserDelete,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    인증된 사용자의 계정을 삭제합니다.
    
    - **password**: 현재 비밀번호 (확인용)
    
    계정 삭제 시 다음 작업이 수행됩니다:
    1. 비밀번호 확인
    2. 모든 리프레시 토큰 무효화
    3. 사용자 계정 삭제
    
    ⚠️ 이 작업은 되돌릴 수 없습니다.
    """
    try:
        # 현재 사용자 정보 조회
        user_data = await get_user_by_id(current_user["id"])
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": {
                        "code": "USER_NOT_FOUND",
                        "message": "사용자를 찾을 수 없습니다.",
                        "details": {}
                    }
                }
            )
        
        # 비밀번호 확인
        if not verify_password(delete_data.password, user_data["password_hash"]):
            logger.warning(f"회원탈퇴 실패 - 잘못된 비밀번호: user_id={current_user['id']}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": {
                        "code": "INVALID_PASSWORD",
                        "message": "비밀번호가 올바르지 않습니다.",
                        "details": {
                            "field": "password",
                            "issue": "계정 삭제를 위해 올바른 비밀번호를 입력해주세요."
                        }
                    }
                }
            )
        
        # 사용자의 모든 리프레시 토큰 무효화
        await delete_user_refresh_tokens(current_user["id"])
        
        # 사용자 계정 삭제
        success = await delete_user(current_user["id"])
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": {
                        "code": "DELETE_FAILED",
                        "message": "계정 삭제에 실패했습니다.",
                        "details": {}
                    }
                }
            )
        
        logger.info(f"회원탈퇴 성공: user_id={current_user['id']}, email={current_user['email']}")
        
        return SuccessResponse(
            message="계정이 성공적으로 삭제되었습니다. 그동안 서비스를 이용해 주셔서 감사합니다.",
            data={
                "deleted_user_id": current_user["id"],
                "deleted_at": "now",
                "message": "모든 개인정보와 관련 데이터가 삭제되었습니다."
            }
        )
        
    except HTTPException:
        raise
    except ValidationError as e:
        logger.error(f"회원탈퇴 데이터 검증 오류: {e}")
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
        logger.error(f"회원탈퇴 서버 오류: {e}")
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
    "/account/verify-password",
    summary="비밀번호 확인",
    description="계정 삭제 전 비밀번호를 확인합니다.",
    responses={
        200: {
            "description": "비밀번호 확인 성공",
            "content": {
                "application/json": {
                    "example": {
                        "verified": True,
                        "message": "비밀번호가 확인되었습니다."
                    }
                }
            }
        },
        401: {
            "description": "인증 실패",
            "model": ErrorResponse
        },
        403: {
            "description": "비밀번호 불일치",
            "model": ErrorResponse
        }
    }
)
async def verify_password_for_deletion(
    password_data: UserDelete,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    계정 삭제 전 비밀번호를 확인합니다.
    
    - **password**: 확인할 현재 비밀번호
    
    실제 삭제는 수행하지 않고 비밀번호만 확인합니다.
    """
    try:
        # 현재 사용자 정보 조회
        user_data = await get_user_by_id(current_user["id"])
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": {
                        "code": "USER_NOT_FOUND",
                        "message": "사용자를 찾을 수 없습니다.",
                        "details": {}
                    }
                }
            )
        
        # 비밀번호 확인
        if not verify_password(password_data.password, user_data["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": {
                        "code": "INVALID_PASSWORD",
                        "message": "비밀번호가 올바르지 않습니다.",
                        "details": {
                            "field": "password",
                            "issue": "올바른 비밀번호를 입력해주세요."
                        }
                    }
                }
            )
        
        return {
            "verified": True,
            "message": "비밀번호가 확인되었습니다."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"비밀번호 확인 오류: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "비밀번호 확인 중 오류가 발생했습니다.",
                    "details": {}
                }
            }
        )

@router.get(
    "/account/deletion-info",
    summary="계정 삭제 안내",
    description="계정 삭제 시 삭제되는 데이터에 대한 안내를 제공합니다.",
    responses={
        200: {
            "description": "계정 삭제 안내 정보",
            "content": {
                "application/json": {
                    "example": {
                        "warning": "계정 삭제는 되돌릴 수 없습니다.",
                        "deleted_data": [
                            "개인정보 (이름, 이메일)",
                            "로그인 기록",
                            "모든 토큰"
                        ],
                        "process": [
                            "비밀번호 확인",
                            "모든 세션 무효화",
                            "계정 및 관련 데이터 삭제"
                        ]
                    }
                }
            }
        },
        401: {
            "description": "인증 실패",
            "model": ErrorResponse
        }
    }
)
async def get_deletion_info(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    계정 삭제 시 삭제되는 데이터와 과정에 대한 안내를 제공합니다.
    """
    return {
        "warning": "⚠️ 계정 삭제는 되돌릴 수 없습니다.",
        "deleted_data": [
            "개인정보 (이름, 이메일)",
            "계정 생성 및 수정 기록",
            "모든 로그인 토큰 및 세션"
        ],
        "process": [
            "1. 현재 비밀번호 확인",
            "2. 모든 활성 세션 무효화",
            "3. 계정 및 관련 데이터 완전 삭제"
        ],
        "alternatives": [
            "계정을 일시적으로 비활성화하고 싶다면 고객센터에 문의하세요.",
            "특정 데이터만 삭제하고 싶다면 개별 설정을 확인하세요."
        ],
        "user_info": {
            "current_email": current_user["email"],
            "member_since": current_user["created_at"].strftime("%Y-%m-%d")
        }
    }