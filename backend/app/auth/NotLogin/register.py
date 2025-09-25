"""
회원가입 API 엔드포인트 (인증 불필요)
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import ValidationError
from ..models import UserRegister, SuccessResponse, ErrorResponse
from ..utils import create_user, check_email_exists
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication - No Login Required"])

@router.post(
    "/register",
    response_model=SuccessResponse,
    status_code=status.HTTP_201_CREATED,
    summary="회원가입",
    description="새로운 사용자 계정을 생성합니다.",
    responses={
        201: {
            "description": "회원가입 성공",
            "model": SuccessResponse
        },
        400: {
            "description": "잘못된 요청 데이터",
            "model": ErrorResponse
        },
        409: {
            "description": "이메일 중복",
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
async def register_user(user_data: UserRegister):
    """
    새로운 사용자 계정을 생성합니다.
    
    - **email**: 유효한 이메일 주소 (중복 불가)
    - **password**: 8자 이상, 대소문자, 숫자, 특수문자 포함
    - **name**: 2-50자, 한글/영문/숫자만 허용
    """
    try:
        # 이메일 중복 확인
        if await check_email_exists(user_data.email):
            logger.warning(f"회원가입 시도 - 중복 이메일: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "error": {
                        "code": "EMAIL_ALREADY_EXISTS",
                        "message": "이미 사용 중인 이메일입니다.",
                        "details": {
                            "field": "email",
                            "issue": "중복된 이메일 주소입니다."
                        }
                    }
                }
            )
        
        # 사용자 생성
        user_id = await create_user(
            email=user_data.email,
            password=user_data.password,
            name=user_data.name
        )
        
        logger.info(f"새 사용자 등록 성공: user_id={user_id}, email={user_data.email}")
        
        return SuccessResponse(
            message="회원가입이 성공적으로 완료되었습니다.",
            data={
                "user_id": user_id,
                "email": user_data.email,
                "name": user_data.name
            }
        )
        
    except HTTPException:
        raise
    except ValidationError as e:
        logger.error(f"회원가입 데이터 검증 오류: {e}")
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
    except ValueError as e:
        logger.error(f"회원가입 비즈니스 로직 오류: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "BUSINESS_LOGIC_ERROR",
                    "message": str(e),
                    "details": {}
                }
            }
        )
    except Exception as e:
        logger.error(f"회원가입 서버 오류: {e}")
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
    "/check-email/{email}",
    summary="이메일 중복 확인",
    description="이메일 주소의 사용 가능 여부를 확인합니다.",
    responses={
        200: {
            "description": "이메일 확인 결과",
            "content": {
                "application/json": {
                    "example": {
                        "available": True,
                        "message": "사용 가능한 이메일입니다."
                    }
                }
            }
        },
        400: {
            "description": "잘못된 이메일 형식",
            "model": ErrorResponse
        }
    }
)
async def check_email_availability(email: str):
    """
    이메일 주소의 사용 가능 여부를 확인합니다.
    
    - **email**: 확인할 이메일 주소
    """
    try:
        # 기본적인 이메일 형식 검증
        if "@" not in email or "." not in email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": {
                        "code": "INVALID_EMAIL_FORMAT",
                        "message": "올바른 이메일 형식이 아닙니다.",
                        "details": {
                            "field": "email",
                            "issue": "이메일 형식을 확인해주세요."
                        }
                    }
                }
            )
        
        # 이메일 중복 확인
        exists = await check_email_exists(email)
        
        return {
            "available": not exists,
            "message": "사용 가능한 이메일입니다." if not exists else "이미 사용 중인 이메일입니다."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"이메일 확인 오류: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "이메일 확인 중 오류가 발생했습니다.",
                    "details": {}
                }
            }
        )