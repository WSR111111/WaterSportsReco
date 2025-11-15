"""
app/config.py
────────────────────────────────────────────
환경설정 관리
"""

import os
from dotenv import load_dotenv
from pathlib import Path

# 프로젝트 루트 디렉토리에서 .env 파일 찾기
project_root = Path(__file__).parent.parent.parent
env_path = project_root / ".env"

load_dotenv(env_path)

# API Keys
KMA_API_KEY = os.getenv("KMA_API_KEY", "")
VITE_KAKAO_API_KEY = os.getenv("VITE_KAKAO_API_KEY", "")
TOURIST_API_KEY = os.getenv("TOURIST_API_KEY", "")

# Database Settings
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT"))
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")


# 기본 개발 환경 CORS 설정
DEFAULT_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173", 
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

ALLOWED_ORIGINS = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "").split(",") if o.strip()] or DEFAULT_ORIGINS


