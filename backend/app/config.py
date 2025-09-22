import os
from dotenv import load_dotenv
from pathlib import Path

# 백엔드 루트 디렉토리에서 .env 파일 찾기
backend_root = Path(__file__).parent.parent
env_path = backend_root / ".env"

load_dotenv(env_path)

# API Keys
KMA_API_KEY = os.getenv("KMA_API_KEY", "")
VITE_KAKAO_API_KEY = os.getenv("VITE_KAKAO_API_KEY", "")
TOURIST_API_KEY = os.getenv("TOURIST_API_KEY", "")

# Database Settings
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "watersportsdb")
MYSQL_USER = os.getenv("MYSQL_USER", "watersports_user")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_ROOT_PASSWORD = os.getenv("MYSQL_ROOT_PASSWORD", "")

# 기본 개발 환경 CORS 설정
DEFAULT_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173", 
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

ALLOWED_ORIGINS = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "").split(",") if o.strip()] or DEFAULT_ORIGINS


