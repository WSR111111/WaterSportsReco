"""
사용자 인증 시스템 데이터 모델
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
import re

class UserBase(BaseModel):
    """사용자 기본 모델"""
    email: EmailStr = Field(..., description="사용자 이메일")
    name: str = Field(..., min_length=2, max_length=50, description="사용자 이름")

class UserRegister(UserBase):
    """회원가입 요청 모델"""
    password: str = Field(..., min_length=8, max_length=128, description="비밀번호")
    
    @validator('password')
    def validate_password(cls, v):
        """비밀번호 정책 검증"""
        if len(v) < 8:
            raise ValueError('비밀번호는 최소 8자 이상이어야 합니다.')
        
        if not re.search(r'[A-Z]', v):
            raise ValueError('비밀번호에는 대문자가 포함되어야 합니다.')
        
        if not re.search(r'[a-z]', v):
            raise ValueError('비밀번호에는 소문자가 포함되어야 합니다.')
        
        if not re.search(r'\d', v):
            raise ValueError('비밀번호에는 숫자가 포함되어야 합니다.')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('비밀번호에는 특수문자가 포함되어야 합니다.')
        
        return v
    
    @validator('name')
    def validate_name(cls, v):
        """이름 검증"""
        if not v.strip():
            raise ValueError('이름은 공백일 수 없습니다.')
        
        # 한글, 영문, 숫자만 허용
        if not re.match(r'^[가-힣a-zA-Z0-9\s]+$', v):
            raise ValueError('이름은 한글, 영문, 숫자만 사용할 수 있습니다.')
        
        return v.strip()

class UserLogin(BaseModel):
    """로그인 요청 모델"""
    email: EmailStr = Field(..., description="사용자 이메일")
    password: str = Field(..., description="비밀번호")

class UserUpdate(BaseModel):
    """회원정보 수정 요청 모델"""
    name: Optional[str] = Field(None, min_length=2, max_length=50, description="새 이름")
    password: Optional[str] = Field(None, min_length=8, max_length=128, description="새 비밀번호")
    current_password: str = Field(..., description="현재 비밀번호")
    
    @validator('password')
    def validate_password(cls, v):
        """새 비밀번호 정책 검증"""
        if v is None:
            return v
        
        if len(v) < 8:
            raise ValueError('비밀번호는 최소 8자 이상이어야 합니다.')
        
        if not re.search(r'[A-Z]', v):
            raise ValueError('비밀번호에는 대문자가 포함되어야 합니다.')
        
        if not re.search(r'[a-z]', v):
            raise ValueError('비밀번호에는 소문자가 포함되어야 합니다.')
        
        if not re.search(r'\d', v):
            raise ValueError('비밀번호에는 숫자가 포함되어야 합니다.')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('비밀번호에는 특수문자가 포함되어야 합니다.')
        
        return v
    
    @validator('name')
    def validate_name(cls, v):
        """새 이름 검증"""
        if v is None:
            return v
        
        if not v.strip():
            raise ValueError('이름은 공백일 수 없습니다.')
        
        # 한글, 영문, 숫자만 허용
        if not re.match(r'^[가-힣a-zA-Z0-9\s]+$', v):
            raise ValueError('이름은 한글, 영문, 숫자만 사용할 수 있습니다.')
        
        return v.strip()

class UserDelete(BaseModel):
    """회원탈퇴 요청 모델"""
    password: str = Field(..., description="현재 비밀번호")

class User(UserBase):
    """사용자 정보 응답 모델"""
    id: int = Field(..., description="사용자 ID")
    created_at: datetime = Field(..., description="생성일시")
    updated_at: datetime = Field(..., description="수정일시")
    
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    """토큰 응답 모델"""
    access_token: str = Field(..., description="액세스 토큰")
    refresh_token: str = Field(..., description="리프레시 토큰")
    token_type: str = Field(default="bearer", description="토큰 타입")
    expires_in: int = Field(..., description="액세스 토큰 만료 시간(초)")

class TokenRefresh(BaseModel):
    """토큰 갱신 요청 모델"""
    refresh_token: str = Field(..., description="리프레시 토큰")

class ErrorResponse(BaseModel):
    """에러 응답 모델"""
    error: dict = Field(..., description="에러 정보")
    
    class Config:
        schema_extra = {
            "example": {
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "입력 데이터가 올바르지 않습니다.",
                    "details": {
                        "field": "email",
                        "issue": "이미 사용 중인 이메일입니다."
                    }
                }
            }
        }

class SuccessResponse(BaseModel):
    """성공 응답 모델"""
    message: str = Field(..., description="성공 메시지")
    data: Optional[dict] = Field(None, description="응답 데이터")
    
    class Config:
        schema_extra = {
            "example": {
                "message": "작업이 성공적으로 완료되었습니다.",
                "data": {}
            }
        }