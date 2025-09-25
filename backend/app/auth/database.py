"""
MySQL 데이터베이스 연결 및 관리 모듈
"""

import os
import mysql.connector
from mysql.connector import pooling, Error
from typing import Optional, Dict, Any
import logging
from contextlib import contextmanager

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """MySQL 데이터베이스 연결 풀 관리 클래스"""
    
    def __init__(self):
        self.pool = None
        self._create_connection_pool()
    
    def _create_connection_pool(self):
        """데이터베이스 연결 풀 생성"""
        try:
            config = {
                'host': os.getenv('MYSQL_HOST', 'localhost'),
                'port': int(os.getenv('MYSQL_PORT', 3307)),
                'database': os.getenv('MYSQL_DATABASE', 'watersports'),
                'user': os.getenv('MYSQL_USER', 'wsuser'),
                'password': os.getenv('MYSQL_PASSWORD', 'wspass'),
                'charset': 'utf8mb4',
                'collation': 'utf8mb4_unicode_ci',
                'autocommit': True,
                'pool_name': 'auth_pool',
                'pool_size': 10,
                'pool_reset_session': True
            }
            
            self.pool = pooling.MySQLConnectionPool(**config)
            logger.info("데이터베이스 연결 풀이 성공적으로 생성되었습니다.")
            
        except Error as e:
            logger.error(f"데이터베이스 연결 풀 생성 실패: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """연결 풀에서 연결을 가져오는 컨텍스트 매니저"""
        connection = None
        try:
            connection = self.pool.get_connection()
            yield connection
        except Error as e:
            logger.error(f"데이터베이스 연결 오류: {e}")
            if connection:
                connection.rollback()
            raise
        finally:
            if connection and connection.is_connected():
                connection.close()
    
    def test_connection(self) -> bool:
        """데이터베이스 연결 테스트"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                cursor.close()
                logger.info("데이터베이스 연결 테스트 성공")
                return result[0] == 1
        except Error as e:
            logger.error(f"데이터베이스 연결 테스트 실패: {e}")
            return False
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> Optional[Any]:
        """SELECT 쿼리 실행"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute(query, params or ())
                result = cursor.fetchall()
                cursor.close()
                return result
        except Error as e:
            logger.error(f"쿼리 실행 오류: {e}")
            raise
    
    def execute_single_query(self, query: str, params: Optional[tuple] = None) -> Optional[Dict[str, Any]]:
        """단일 결과 SELECT 쿼리 실행"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute(query, params or ())
                result = cursor.fetchone()
                cursor.close()
                return result
        except Error as e:
            logger.error(f"단일 쿼리 실행 오류: {e}")
            raise
    
    def execute_update(self, query: str, params: Optional[tuple] = None) -> int:
        """INSERT, UPDATE, DELETE 쿼리 실행"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params or ())
                affected_rows = cursor.rowcount
                last_id = cursor.lastrowid
                cursor.close()
                conn.commit()
                return last_id if last_id else affected_rows
        except Error as e:
            logger.error(f"업데이트 쿼리 실행 오류: {e}")
            raise

# 전역 데이터베이스 매니저 인스턴스
db_manager = DatabaseManager()

def get_db_manager() -> DatabaseManager:
    """데이터베이스 매니저 인스턴스 반환"""
    return db_manager