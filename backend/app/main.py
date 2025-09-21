from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from .services.sync_service import (
    sync_marine_stations, sync_surface_stations,
    sync_leisure_places, sync_categories, sync_place_details, sync_regions, sync_ground_stations
)

app = FastAPI(title="Marine Conditions API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#=============================================================================
# ✅ 데이터 동기화 API (관리자 / 스케줄러 용도)
#=============================================================================

@app.post("/api/sync/marine")
async def sync_marine_data(tm: str | None = Query(None)):
    """해양 관측소 데이터 동기화"""
    return await sync_marine_stations(tm)

@app.post("/api/sync/surface")
async def sync_surface_data(tm: str | None = Query(None)):
    """지상 관측소 데이터 동기화"""
    return await sync_surface_stations(tm)

@app.post("/api/sync/leisure-places")
async def sync_leisure_places_data(
    area_code: str | None = Query(None),
    sigungu_code: str | None = Query(None)
):
    """레저 장소 데이터 동기화"""
    return await sync_leisure_places(area_code, sigungu_code)

@app.post("/api/sync/place-details")
async def sync_place_details_data(
    limit: int = Query(10, description="처리할 최대 content_id 수 (API 제한 고려)"),
    delay: int = Query(3, description="API 호출 간 대기 시간(초)")
):
    """장소 상세정보 동기화 (API 제한 고려하여 소량씩 처리)"""
    return await sync_place_details(limit, delay)

@app.post("/api/sync/categories")
async def sync_category_data():
    """카테고리 코드 데이터 동기화"""
    return await sync_categories("28", "A03", "A0303")

@app.post("/api/sync/regions")
async def sync_regions_data():
    """한국관광공사 행정구역 데이터 동기화"""
    return await sync_regions()

@app.post("/api/sync/ground-stations")
async def sync_ground_stations_data():
    """지상 관측소 정보 동기화"""
    return await sync_ground_stations()


