from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from .services.db.manager import DatabaseManager
from .services.sync.sync_marine_service import SyncMarineService
from .services.sync.sync_surface_service import SyncSurfaceService
from .services.sync.sync_leisure_service import SyncLeisureService
from .services.sync.sync_category_service import SyncCategoryService
from .services.sync.sync_region_service import SyncRegionService
from .services.sync.sync_place_detail_service import SyncPlaceDetailService
from .services.sync.sync_ground_station_service import SyncGroundStationService

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


@app.post("/api/sync/regions")
async def sync_regions_data():
    """지역 데이터 동기화"""
    db_manager = DatabaseManager()
    await db_manager.connect()
    
    try:
        service = SyncRegionService(db_manager)
        # 기본 지역 코드들 (예시)
        region_codes = [
            {"sigungu_code": "1", "area_code": "1"},
            {"sigungu_code": "2", "area_code": "1"},
            # 필요한 지역 코드들 추가
        ]
        return await service.sync_regions_from_codes(region_codes)
    finally:
        await db_manager.disconnect()


@app.post("/api/sync/categories")
async def sync_category_data():
    """카테고리 코드 데이터 동기화"""
    db_manager = DatabaseManager()
    await db_manager.connect()
    
    try:
        async with SyncCategoryService(db_manager) as service:
            return await service.sync_category_data("28", "A03", "A0303")
    finally:
        await db_manager.disconnect()

@app.post("/api/sync/ground-stations")
async def sync_ground_stations_data(tm: str | None = Query(None)):
    """지상 관측소 정보 동기화"""
    db_manager = DatabaseManager()
    await db_manager.connect()
    
    try:
        async with SyncGroundStationService(db_manager) as service:
            return await service.sync_ground_stations_data(tm)
    finally:
        await db_manager.disconnect()

@app.post("/api/sync/surface")
async def sync_surface_data(tm: str | None = Query(None)):
    """지상 관측 데이터 동기화"""
    db_manager = DatabaseManager()
    await db_manager.connect()
    
    try:
        async with SyncSurfaceService(db_manager) as service:
            return await service.sync_surface_data(tm)
    finally:
        await db_manager.disconnect()

@app.post("/api/sync/marine")
async def sync_marine_data(tm: str | None = Query(None)):
    """해양 관측소 + 해양관측 데이터 동기화"""
    db_manager = DatabaseManager()
    await db_manager.connect()
    
    try:
        async with SyncMarineService(db_manager) as service:
            return await service.sync_marine_data(tm)
    finally:
        await db_manager.disconnect()


@app.post("/api/sync/leisure-places")
async def sync_leisure_places_data(
    area_code: str | None = Query(None),
    sigungu_code: str | None = Query(None)
):
    """레저 장소 데이터 동기화"""
    db_manager = DatabaseManager()
    await db_manager.connect()
    
    try:
        async with SyncLeisureService(db_manager) as service:
            return await service.sync_leisure_places_data(area_code, sigungu_code)
    finally:
        await db_manager.disconnect()


@app.post("/api/sync/place-details")
async def sync_place_details_data(
    limit: int = Query(10, description="처리할 최대 content_id 수 (API 제한 고려)"),
    delay: int = Query(3, description="API 호출 간 대기 시간(초)")
):
    """장소 상세정보 동기화 (API 제한 고려하여 소량씩 처리)"""
    db_manager = DatabaseManager()
    await db_manager.connect()
    
    try:
        async with SyncPlaceDetailService(db_manager) as service:
            return await service.sync_place_details_data(limit, delay)
    finally:
        await db_manager.disconnect()



