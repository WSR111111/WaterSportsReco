"""
app/database.py
────────────────────────────────────────────
PostgreSQL 연결 및 쿼리 실행 관리 모듈

"""

import psycopg2
from psycopg2 import pool, Error
from psycopg2.extras import RealDictCursor
from app.config import (
    POSTGRES_HOST,
    POSTGRES_PORT,
    POSTGRES_DB,
    POSTGRES_USER,
    POSTGRES_PASSWORD,
)
from typing import Optional, Dict, Any, List
import logging
from contextlib import contextmanager

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseManager:
    """PostgreSQL 데이터베이스 연결 풀 관리"""

    def __init__(self):
        self.pool = None
        self._create_connection_pool()

    def _create_connection_pool(self):
        """데이터베이스 연결 풀 생성"""
        try:
            if not POSTGRES_PASSWORD:
                raise ValueError("POSTGRES_PASSWORD environment variable is required for security")

            self.pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=1,
                maxconn=10,
                host=POSTGRES_HOST,
                database=POSTGRES_DB,
                user=POSTGRES_USER,
                password=POSTGRES_PASSWORD,
                port=POSTGRES_PORT,
                cursor_factory=RealDictCursor
            )
            logger.info("PostgreSQL 데이터베이스 연결 풀이 성공적으로 생성되었습니다.")

        except Error as e:
            logger.error(f"데이터베이스 연결 풀 생성 실패: {e}")
            raise

    @contextmanager
    def get_connection(self):
        """연결 풀에서 연결을 가져오는 컨텍스트 매니저"""
        connection = None
        try:
            connection = self.pool.getconn()
            yield connection
        except Error as e:
            logger.error(f"데이터베이스 연결 오류: {e}")
            if connection:
                connection.rollback()
            raise
        finally:
            if connection:
                self.pool.putconn(connection)

    def connect(self):
        """레거시 호환성을 위한 연결 메서드"""
        logger.warning("connect() 메서드는 deprecated입니다. get_connection() 컨텍스트 매니저를 사용하세요.")
        return self.pool.getconn()

    def disconnect(self):
        """레거시 호환성을 위한 연결 해제 메서드"""
        logger.warning("disconnect() 메서드는 deprecated입니다. get_connection() 컨텍스트 매니저를 사용하세요.")
        pass

    def test_connection(self) -> bool:
        """데이터베이스 연결 테스트"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    result = cursor.fetchone()
                    logger.info("데이터베이스 연결 테스트 성공")
                    return result[0] == 1
        except Error as e:
            logger.error(f"데이터베이스 연결 테스트 실패: {e}")
            return False

    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """다중 결과 SELECT 쿼리 실행"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, params or ())
                    result = cursor.fetchall()
                    return [dict(row) for row in result]
        except Error as e:
            logger.error(f"쿼리 실행 오류: {e}")
            raise

    def execute_single_query(self, query: str, params: tuple = None) -> Optional[Dict[str, Any]]:
        """단일 결과 SELECT 쿼리 실행"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, params or ())
                    result = cursor.fetchone()
                    return dict(result) if result else None
        except Error as e:
            logger.error(f"단일 쿼리 실행 오류: {e}")
            raise

    def execute_non_query(self, query: str, params: tuple = None) -> bool:
        """레거시 호환성을 위한 INSERT, UPDATE, DELETE 쿼리 실행"""
        try:
            result = self.execute_update(query, params)
            return result is not None
        except Error as e:
            logger.error(f"Non-query 실행 오류: {e}")
            raise

    def execute_update(self, query: str, params: tuple = None) -> int:
        """INSERT, UPDATE, DELETE 쿼리 실행"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, params or ())
                    affected_rows = cursor.rowcount
                    conn.commit()
                    return affected_rows
        except Error as e:
            logger.error(f"업데이트 쿼리 실행 오류: {e}")
            raise

    def close_all_connections(self):
        """모든 연결 풀 종료"""
        if self.pool:
            self.pool.closeall()
            logger.info("모든 데이터베이스 연결이 종료되었습니다.")


# 전역 데이터베이스 매니저 인스턴스
db_manager = DatabaseManager()


def get_db_manager() -> DatabaseManager:
    """데이터베이스 매니저 인스턴스 반환"""
    return db_manager