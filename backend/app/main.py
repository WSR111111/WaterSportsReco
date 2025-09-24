from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 라우터 import
from app.api.routes_region import router as region_router
from app.api.routes_station import router as station_router
from app.api.routes_observation import router as observation_router
from app.api.routes_sports import router as sports_router
from app.api.routes_leisure import router as leisure_router

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
app.include_router(region_router, prefix="/api", tags=["Region"])
app.include_router(station_router, prefix="/api", tags=["Station"])
app.include_router(observation_router, prefix="/api", tags=["Observation"])
app.include_router(sports_router, prefix="/api", tags=["Sports"])
app.include_router(leisure_router, prefix="/api", tags=["Leisure"])


@app.get("/")
def root():
    return {"message": "Water Sports API is running 🚀"}
