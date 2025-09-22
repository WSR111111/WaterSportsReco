import os
from dotenv import load_dotenv
from pathlib import Path

# 백엔드 루트 디렉토리에서 .env 파일 찾기
backend_root = Path(__file__).parent.parent
env_path = backend_root / ".env"

load_dotenv(env_path)

KMA_API_KEY = os.getenv("KMA_API_KEY", "")
KAKAO_API_KEY = os.getenv("KAKAO_API_KEY", "")
TOURIST_API_KEY = os.getenv("TOURIST_API_KEY", "")
# 기본 개발 환경 CORS 설정
DEFAULT_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173", 
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

ALLOWED_ORIGINS = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "").split(",") if o.strip()] or DEFAULT_ORIGINS


