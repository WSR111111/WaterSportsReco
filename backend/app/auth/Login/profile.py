"""
회원정보 수정 API 엔드포인트 (인증 필요)
"""

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import ValidationError
from typing import Dict, Any
from ..models import UserUpdate, User, SuccessResponse, ErrorResponse
from ..middleware import get_current_user
from ..utils import update_user_info, verify_password, get_user_by_id
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication - Login Required"])

@router.put(
    "/profile",
    response_model=SuccessResponse,
    summary="회원정보 수정",
    description="인증된 사용자의 정보를 수정합니다.",
    responses={
        200: {
            "description": "정보 수정 성공",
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
            "description": "현재 비밀번호 불일치",
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
async def update_profile(
    update_data: UserUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    인증된 사용자의 정보를 수정합니다.
    
    - **name**: 새로운 이름 (선택사항)
    - **password**: 새로운 비밀번호 (선택사항)
    - **current_password**: 현재 비밀번호 (필수)
    
    이름 또는 비밀번호 중 하나 이상을 변경해야 합니다.
    """
    try:
        # 현재 비밀번호 확인
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
        
        if not verify_password(update_data.current_password, user_data["password_hash"]):
            logger.warning(f"회원정보 수정 실패 - 잘못된 현재 비밀번호: user_id={current_user['id']}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": {
                        "code": "INVALID_CURRENT_PASSWORD",
                        "message": "현재 비밀번호가 올바르지 않습니다.",
                        "details": {
                            "field": "current_password",
                            "issue": "비밀번호를 확인해주세요."
                        }
                    }
                }
            )
        
        # 변경할 내용이 있는지 확인
        if not update_data.name and not update_data.password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": {
                        "code": "NO_CHANGES_REQUESTED",
                        "message": "변경할 정보를 입력해주세요.",
                        "details": {
                            "issue": "이름 또는 비밀번호 중 하나 이상을 변경해야 합니다."
                        }
                    }
                }
            )
        
        # 사용자 정보 업데이트
        success = await update_user_info(
            user_id=current_user["id"],
            name=update_data.name,
            password=update_data.password
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": {
                        "code": "UPDATE_FAILED",
                        "message": "정보 수정에 실패했습니다.",
                        "details": {}
                    }
                }
            )
        
        # 변경된 정보 구성
        updated_fields = []
        if update_data.name:
            updated_fields.append("이름")
        if update_data.password:
            updated_fields.append("비밀번호")
        
        logger.info(f"회원정보 수정 성공: user_id={current_user['id']}, fields={updated_fields}")
        
        return SuccessResponse(
            message=f"{', '.join(updated_fields)}이(가) 성공적으로 수정되었습니다.",
            data={
                "user_id": current_user["id"],
                "updated_fields": updated_fields,
                "updated_at": "now"
            }
        )
        
    except HTTPException:
        raise
    except ValidationError as e:
        logger.error(f"회원정보 수정 데이터 검증 오류: {e}")
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
        logger.error(f"회원정보 수정 서버 오류: {e}")
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

@router.get(
    "/me",
    response_model=User,
    summary="현재 사용자 정보 조회",
    description="인증된 사용자의 정보를 조회합니다.",
    responses={
        200: {
            "description": "사용자 정보 조회 성공",
            "model": User
        },
        401: {
            "description": "인증 실패",
            "model": ErrorResponse
        },
        404: {
            "description": "사용자를 찾을 수 없음",
            "model": ErrorResponse
        },
        500: {
            "description": "서버 내부 오류",
            "model": ErrorResponse
        }
    }
)
async def get_current_user_info(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    현재 인증된 사용자의 정보를 조회합니다.
    
    JWT 토큰에서 추출한 사용자 정보를 반환합니다.
    """
    try:
        # 최신 사용자 정보 조회
        user_data = await get_user_by_id(current_user["id"])
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "USER_NOT_FOUND",
                        "message": "사용자를 찾을 수 없습니다.",
                        "details": {}
                    }
                }
            )
        
        # 비밀번호 해시 제거
        user_info = {k: v for k, v in user_data.items() if k != 'password_hash'}
        
        return User(**user_info)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"사용자 정보 조회 오류: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "사용자 정보 조회 중 오류가 발생했습니다.",
                    "details": {}
                }
            }
        )

@router.get(
    "/profile/summary",
    summary="사용자 프로필 요약",
    description="사용자의 기본 프로필 정보를 요약해서 반환합니다.",
    responses={
        200: {
            "description": "프로필 요약 정보",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "name": "홍길동",
                        "email": "user@example.com",
                        "member_since": "2024-01-01",
                        "last_login": "2024-01-15T10:30:00Z"
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
async def get_profile_summary(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    사용자의 기본 프로필 정보를 요약해서 반환합니다.
    
    민감하지 않은 기본 정보만 포함됩니다.
    """
    try:
        return {
            "id": current_user["id"],
            "name": current_user["name"],
            "email": current_user["email"],
            "member_since": current_user["created_at"].strftime("%Y-%m-%d"),
            "last_updated": current_user["updated_at"].strftime("%Y-%m-%d %H:%M:%S")
        }
        
    except Exception as e:
        logger.error(f"프로필 요약 조회 오류: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "프로필 정보 조회 중 오류가 발생했습니다.",
                    "details": {}
                }
            }
        )