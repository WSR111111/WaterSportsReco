"""
JWT 토큰 생성, 검증, 갱신 관리 모듈
"""

import os
import jwt
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from .utils import hash_token, save_refresh_token, verify_refresh_token, delete_refresh_token
import logging

logger = logging.getLogger(__name__)

# JWT 설정
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRE_MINUTES', 15))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv('JWT_REFRESH_TOKEN_EXPIRE_DAYS', 1))

if not JWT_SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY 환경변수가 설정되지 않았습니다.")

class JWTHandler:
    """JWT 토큰 관리 클래스"""
    
    @staticmethod
    def create_access_token(data: Dict[str, Any]) -> str:
        """액세스 토큰 생성"""
        try:
            to_encode = data.copy()
            expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            
            to_encode.update({
                "exp": expire,
                "iat": datetime.now(timezone.utc),
                "type": "access"
            })
            
            encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
            return encoded_jwt
            
        except Exception as e:
            logger.error(f"액세스 토큰 생성 오류: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="토큰 생성에 실패했습니다."
            )
    
    @staticmethod
    def create_refresh_token() -> str:
        """리프레시 토큰 생성 (랜덤 문자열)"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    async def create_token_pair(user_data: Dict[str, Any]) -> Dict[str, Any]:
        """액세스 토큰과 리프레시 토큰 쌍 생성"""
        try:
            # 액세스 토큰 생성
            access_token_data = {
                "sub": str(user_data["id"]),
                "email": user_data["email"],
                "name": user_data["name"]
            }
            access_token = JWTHandler.create_access_token(access_token_data)
            
            # 리프레시 토큰 생성
            refresh_token = JWTHandler.create_refresh_token()
            refresh_token_hash = hash_token(refresh_token)
            
            # 리프레시 토큰 만료 시간
            expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
            
            # 리프레시 토큰 데이터베이스에 저장
            await save_refresh_token(user_data["id"], refresh_token_hash, expires_at)
            
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
            }
            
        except Exception as e:
            logger.error(f"토큰 쌍 생성 오류: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="토큰 생성에 실패했습니다."
            )
    
    @staticmethod
    def verify_access_token(token: str) -> Dict[str, Any]:
        """액세스 토큰 검증"""
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            
            # 토큰 타입 확인
            if payload.get("type") != "access":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="잘못된 토큰 타입입니다."
                )
            
            # 필수 필드 확인
            user_id = payload.get("sub")
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="토큰에 사용자 정보가 없습니다."
                )
            
            return {
                "user_id": int(user_id),
                "email": payload.get("email"),
                "name": payload.get("name")
            }
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="토큰이 만료되었습니다."
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않은 토큰입니다."
            )
        except Exception as e:
            logger.error(f"액세스 토큰 검증 오류: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="토큰 검증에 실패했습니다."
            )
    
    @staticmethod
    async def refresh_access_token(refresh_token: str) -> Dict[str, Any]:
        """리프레시 토큰으로 새 액세스 토큰 발급"""
        try:
            # 리프레시 토큰 해싱
            token_hash = hash_token(refresh_token)
            
            # 데이터베이스에서 토큰 검증
            user_id = await verify_refresh_token(token_hash)
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="유효하지 않거나 만료된 리프레시 토큰입니다."
                )
            
            # 사용자 정보 조회
            from .utils import get_user_by_id
            user_data = await get_user_by_id(user_id)
            if not user_data:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="사용자를 찾을 수 없습니다."
                )
            
            # 새 액세스 토큰 생성
            access_token_data = {
                "sub": str(user_data["id"]),
                "email": user_data["email"],
                "name": user_data["name"]
            }
            new_access_token = JWTHandler.create_access_token(access_token_data)
            
            return {
                "access_token": new_access_token,
                "token_type": "bearer",
                "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"토큰 갱신 오류: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="토큰 갱신에 실패했습니다."
            )
    
    @staticmethod
    async def revoke_refresh_token(refresh_token: str) -> bool:
        """리프레시 토큰 무효화"""
        try:
            token_hash = hash_token(refresh_token)
            return await delete_refresh_token(token_hash)
        except Exception as e:
            logger.error(f"토큰 무효화 오류: {e}")
            return False
    
    @staticmethod
    def get_token_expiry_info(token: str) -> Dict[str, Any]:
        """토큰 만료 정보 조회 (검증 없이)"""
        try:
            # 검증 없이 디코딩 (만료된 토큰도 정보 확인 가능)
            payload = jwt.decode(token, options={"verify_signature": False})
            
            exp = payload.get("exp")
            iat = payload.get("iat")
            
            if exp:
                exp_datetime = datetime.fromtimestamp(exp, tz=timezone.utc)
                now = datetime.now(timezone.utc)
                
                return {
                    "expires_at": exp_datetime,
                    "issued_at": datetime.fromtimestamp(iat, tz=timezone.utc) if iat else None,
                    "is_expired": now > exp_datetime,
                    "time_until_expiry": (exp_datetime - now).total_seconds() if now <= exp_datetime else 0
                }
            
            return {"error": "토큰에 만료 정보가 없습니다."}
            
        except Exception as e:
            logger.error(f"토큰 정보 조회 오류: {e}")
            return {"error": "토큰 정보를 조회할 수 없습니다."}

# 편의 함수들
def create_access_token(data: Dict[str, Any]) -> str:
    """액세스 토큰 생성 편의 함수"""
    return JWTHandler.create_access_token(data)

async def create_token_pair(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """토큰 쌍 생성 편의 함수"""
    return await JWTHandler.create_token_pair(user_data)

def verify_access_token(token: str) -> Dict[str, Any]:
    """액세스 토큰 검증 편의 함수"""
    return JWTHandler.verify_access_token(token)

async def refresh_access_token(refresh_token: str) -> Dict[str, Any]:
    """토큰 갱신 편의 함수"""
    return await JWTHandler.refresh_access_token(refresh_token)