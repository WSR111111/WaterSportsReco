"""
인증 시스템 유틸리티 함수들
"""

import os
import hashlib
from passlib.context import CryptContext
from typing import Optional, Dict, Any
from .database import get_db_manager
from .models import User
import logging

logger = logging.getLogger(__name__)

# 비밀번호 해싱 컨텍스트 설정
pwd_context = CryptContext(
    schemes=["bcrypt"], 
    deprecated="auto",
    bcrypt__rounds=int(os.getenv('BCRYPT_ROUNDS', 12))
)

def hash_password(password: str) -> str:
    """비밀번호 해싱"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """비밀번호 검증"""
    return pwd_context.verify(plain_password, hashed_password)

def hash_token(token: str) -> str:
    """토큰 해싱 (리프레시 토큰 저장용)"""
    return hashlib.sha256(token.encode()).hexdigest()

async def check_email_exists(email: str) -> bool:
    """이메일 중복 확인"""
    try:
        db = get_db_manager()
        query = "SELECT id FROM users WHERE email = %s"
        result = db.execute_single_query(query, (email,))
        return result is not None
    except Exception as e:
        logger.error(f"이메일 중복 확인 오류: {e}")
        raise

async def create_user(email: str, password: str, name: str) -> int:
    """새 사용자 생성"""
    try:
        # 이메일 중복 확인
        if await check_email_exists(email):
            raise ValueError("이미 사용 중인 이메일입니다.")
        
        # 비밀번호 해싱
        hashed_password = hash_password(password)
        
        # 사용자 생성
        db = get_db_manager()
        query = """
        INSERT INTO users (email, password_hash, name) 
        VALUES (%s, %s, %s)
        """
        user_id = db.execute_update(query, (email, hashed_password, name))
        
        logger.info(f"새 사용자 생성 완료: {email}")
        return user_id
        
    except Exception as e:
        logger.error(f"사용자 생성 오류: {e}")
        raise

async def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """이메일로 사용자 조회"""
    try:
        db = get_db_manager()
        query = """
        SELECT id, email, password_hash, name, created_at, updated_at 
        FROM users WHERE email = %s
        """
        result = db.execute_single_query(query, (email,))
        return result
    except Exception as e:
        logger.error(f"사용자 조회 오류: {e}")
        raise

async def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """ID로 사용자 조회"""
    try:
        db = get_db_manager()
        query = """
        SELECT id, email, password_hash, name, created_at, updated_at 
        FROM users WHERE id = %s
        """
        result = db.execute_single_query(query, (user_id,))
        return result
    except Exception as e:
        logger.error(f"사용자 조회 오류: {e}")
        raise

async def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
    """사용자 인증"""
    try:
        user = await get_user_by_email(email)
        if not user:
            return None
        
        if not verify_password(password, user['password_hash']):
            return None
        
        # 비밀번호 해시 제거 후 반환
        user_data = {k: v for k, v in user.items() if k != 'password_hash'}
        return user_data
        
    except Exception as e:
        logger.error(f"사용자 인증 오류: {e}")
        raise

async def update_user_info(user_id: int, name: Optional[str] = None, password: Optional[str] = None) -> bool:
    """사용자 정보 업데이트"""
    try:
        db = get_db_manager()
        
        # 업데이트할 필드 구성
        update_fields = []
        params = []
        
        if name is not None:
            update_fields.append("name = %s")
            params.append(name)
        
        if password is not None:
            update_fields.append("password_hash = %s")
            params.append(hash_password(password))
        
        if not update_fields:
            return True  # 업데이트할 내용이 없음
        
        params.append(user_id)
        
        query = f"""
        UPDATE users 
        SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP 
        WHERE id = %s
        """
        
        affected_rows = db.execute_update(query, tuple(params))
        
        logger.info(f"사용자 정보 업데이트 완료: user_id={user_id}")
        return affected_rows > 0
        
    except Exception as e:
        logger.error(f"사용자 정보 업데이트 오류: {e}")
        raise

async def delete_user(user_id: int) -> bool:
    """사용자 삭제"""
    try:
        db = get_db_manager()
        
        # 관련 리프레시 토큰 먼저 삭제 (외래키 제약조건으로 자동 삭제되지만 명시적으로)
        delete_tokens_query = "DELETE FROM refresh_tokens WHERE user_id = %s"
        db.execute_update(delete_tokens_query, (user_id,))
        
        # 사용자 삭제
        delete_user_query = "DELETE FROM users WHERE id = %s"
        affected_rows = db.execute_update(delete_user_query, (user_id,))
        
        logger.info(f"사용자 삭제 완료: user_id={user_id}")
        return affected_rows > 0
        
    except Exception as e:
        logger.error(f"사용자 삭제 오류: {e}")
        raise

async def save_refresh_token(user_id: int, token_hash: str, expires_at) -> bool:
    """리프레시 토큰 저장"""
    try:
        db = get_db_manager()
        query = """
        INSERT INTO refresh_tokens (user_id, token_hash, expires_at) 
        VALUES (%s, %s, %s)
        """
        result = db.execute_update(query, (user_id, token_hash, expires_at))
        return result > 0
    except Exception as e:
        logger.error(f"리프레시 토큰 저장 오류: {e}")
        raise

async def verify_refresh_token(token_hash: str) -> Optional[int]:
    """리프레시 토큰 검증 및 사용자 ID 반환"""
    try:
        db = get_db_manager()
        query = """
        SELECT user_id FROM refresh_tokens 
        WHERE token_hash = %s AND expires_at > NOW()
        """
        result = db.execute_single_query(query, (token_hash,))
        return result['user_id'] if result else None
    except Exception as e:
        logger.error(f"리프레시 토큰 검증 오류: {e}")
        raise

async def delete_refresh_token(token_hash: str) -> bool:
    """리프레시 토큰 삭제"""
    try:
        db = get_db_manager()
        query = "DELETE FROM refresh_tokens WHERE token_hash = %s"
        affected_rows = db.execute_update(query, (token_hash,))
        return affected_rows > 0
    except Exception as e:
        logger.error(f"리프레시 토큰 삭제 오류: {e}")
        raise

async def delete_user_refresh_tokens(user_id: int) -> bool:
    """사용자의 모든 리프레시 토큰 삭제"""
    try:
        db = get_db_manager()
        query = "DELETE FROM refresh_tokens WHERE user_id = %s"
        affected_rows = db.execute_update(query, (user_id,))
        logger.info(f"사용자 리프레시 토큰 삭제 완료: user_id={user_id}, 삭제된 토큰 수={affected_rows}")
        return True
    except Exception as e:
        logger.error(f"사용자 리프레시 토큰 삭제 오류: {e}")
        raise