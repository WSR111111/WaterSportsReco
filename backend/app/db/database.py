import mysql.connector
from mysql.connector import Error
import os


class DatabaseManager:
    """데이터베이스 연결 및 작업 관리"""
    
    def __init__(self):
        self.connection = None
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
    
    def connect(self):
        """데이터베이스 연결"""
        try:
            self.connection = mysql.connector.connect(**self.db_config)
            return self.connection
        except Error as e:
            print(f"❌ Database connection failed: {e}")
            return None
    
    def disconnect(self):
        """데이터베이스 연결 해제"""
        if self.connection and self.connection.is_connected():
            self.connection.close()

    def execute_query(self, query: str, params: tuple = None):
        """SELECT 쿼리 실행"""
        cursor = self.connection.cursor()
        cursor.execute(query, params or ())
        result = cursor.fetchall()
        cursor.close()
        return result

    def execute_non_query(self, query: str, params: tuple = None):
        """INSERT, UPDATE, DELETE 쿼리 실행"""
        cursor = self.connection.cursor()
        cursor.execute(query, params or ())
        self.connection.commit()
        cursor.close()
        return True
