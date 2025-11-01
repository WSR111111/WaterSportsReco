"""
app/main.py
────────────────────────────────────────────
- FastAPI 인스턴스 생성 (title, description, version 설정)
- CORS 허용 도메인 설정
- 기능별 라우터 등록
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 라우터 import
from app.api.router_index import router as api_router
from app.auth.router import auth_router

from app.config import ALLOWED_ORIGINS

app = FastAPI(
    title="Water Sports API",
    description="수상스포츠 추천 서비스용 API 서버",
    version="1.0.0",
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(api_router, prefix="/api")

# 인증 라우터 등록
app.include_router(auth_router, prefix="/api", tags=["Authentication"])


@app.get("/")
def root():
    return {"message": "Water Sports API is running 🚀"}
