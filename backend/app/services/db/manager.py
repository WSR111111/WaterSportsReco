import mysql.connector
from mysql.connector import Error
import os


class DatabaseManager:
    """데이터베이스 연결 및 작업 관리"""
    
    def __init__(self):
        self.connection = None
        # 환경 변수에서 데이터베이스 설정 로드 (보안상 기본값 없음)
        mysql_password = os.getenv('MYSQL_PASSWORD')
        if not mysql_password:
            raise ValueError("MYSQL_PASSWORD environment variable is required for security")
        
        self.db_config = {
            'host': os.getenv('MYSQL_HOST', 'localhost'),
            'database': os.getenv('MYSQL_DATABASE', 'watersportsdb'),
            'user': os.getenv('MYSQL_USER', 'watersports_user'),
            'password': mysql_password,
            'port': int(os.getenv('MYSQL_PORT', 3306)), 
            'charset': 'utf8mb4',
            'autocommit': True
        }
    
    async def connect(self):
        """데이터베이스 연결"""
        try:
            self.connection = mysql.connector.connect(**self.db_config)
            print("✅ Database connected successfully")
            return True
        except Error as e:
            print(f"❌ Database connection failed: {e}")
            return False
    
    async def disconnect(self):
        """데이터베이스 연결 해제"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("✅ Database disconnected")
    
    async def execute_query(self, query: str, params: tuple = None):
        """쿼리 실행"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            result = cursor.fetchall()
            cursor.close()
            return result
        except Error as e:
            print(f"❌ Query execution failed: {e}")
            return None