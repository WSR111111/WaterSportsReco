from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from .services.db.manager import DatabaseManager
from .services.db.repositories.place_repository import PlaceRepository
from .services.db.repositories.station_repository import StationRepository
from .services.db.repositories.sports_repository import SportsRepository
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
# ✅ 데이터 조회 API (프론트엔드용)
#=============================================================================

@app.get("/api/places")
async def get_places(
    cat3: str | None = Query(None, description="스포츠 카테고리 코드"),
    area_code: str | None = Query(None, description="지역 코드"),
    sigungu_code: str | None = Query(None, description="시군구 코드"),
    limit: int = Query(100, description="최대 조회 개수")
):
    """레저 장소 목록 조회"""
    db_manager = DatabaseManager()
    await db_manager.connect()
    
    try:
        place_repo = PlaceRepository(db_manager)
        
        # 기본 쿼리
        query = """
            SELECT lp.content_id, lp.place_name, lp.address, lp.address2, 
                   lp.phone_number, lp.latitude, lp.longitude, lp.first_image,
                   pd.homepage, pd.overview, s.sport_name, s.category_code
            FROM leisure_place lp
            LEFT JOIN place_detail pd ON lp.content_id = pd.content_id
            LEFT JOIN sports s ON lp.cat3 = s.category_code
            WHERE 1=1
        """
        params = []
        
        # 필터 조건 추가
        if cat3:
            query += " AND lp.cat3 = %s"
            params.append(cat3)
        if area_code:
            query += " AND lp.area_code = %s"
            params.append(area_code)
        if sigungu_code:
            query += " AND lp.sigungu_code = %s"
            params.append(sigungu_code)
            
        query += " ORDER BY lp.place_name LIMIT %s"
        params.append(limit)
        
        result = await db_manager.execute_query(query, tuple(params))
        
        places = []
        for row in result:
            places.append({
                "content_id": row[0],
                "title": row[1],
                "addr1": row[2],
                "addr2": row[3],
                "tel": row[4],
                "mapy": row[5],  # latitude
                "mapx": row[6],  # longitude
                "firstimage": row[7],
                "homepage": row[8],
                "overview": row[9],
                "sport_name": row[10],
                "cat3": row[11]
            })
        
        return {"places": places, "count": len(places)}
        
    finally:
        await db_manager.disconnect()

@app.get("/api/marine-stations")
async def get_marine_stations(limit: int = Query(100, description="최대 조회 개수")):
    """해양 관측소 목록 조회"""
    db_manager = DatabaseManager()
    await db_manager.connect()
    
    try:
        query = """
            SELECT station_id, station_name, latitude, longitude, 
                   observation_time, wave_height, water_temp
            FROM ocean_info
            WHERE observation_time >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
            ORDER BY observation_time DESC
            LIMIT %s
        """
        result = await db_manager.execute_query(query, (limit,))
        
        stations = []
        for row in result:
            stations.append({
                "station_id": row[0],
                "station_name": row[1],
                "lat": float(row[2]) if row[2] else None,
                "lon": float(row[3]) if row[3] else None,
                "observed_at": str(row[4]) if row[4] else None,
                "wave_height": float(row[5]) if row[5] is not None else None,
                "sst": float(row[6]) if row[6] is not None else None
            })
        
        return {"stations": stations, "count": len(stations)}
        
    finally:
        await db_manager.disconnect()

@app.get("/api/surface-stations")
async def get_surface_stations(limit: int = Query(100, description="최대 조회 개수")):
    """지상 관측소 목록 조회"""
    db_manager = DatabaseManager()
    await db_manager.connect()
    
    try:
        query = """
            SELECT gs.station_id, gs.station_name, gs.latitude, gs.longitude,
                   gi.observation_time, gi.wind_speed, gi.temp, gi.humidity
            FROM ground_stations gs
            LEFT JOIN ground_info gi ON gs.station_id = gi.station_id
            WHERE gi.observation_time >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
            ORDER BY gi.observation_time DESC
            LIMIT %s
        """
        result = await db_manager.execute_query(query, (limit,))
        
        stations = []
        for row in result:
            stations.append({
                "station_id": row[0],
                "station_name": row[1],
                "lat": float(row[2]) if row[2] else None,
                "lon": float(row[3]) if row[3] else None,
                "observed_at": str(row[4]) if row[4] else None,
                "wind_speed": float(row[5]) if row[5] is not None else None,
                "temperature": float(row[6]) if row[6] is not None else None,
                "humidity": float(row[7]) if row[7] is not None else None
            })
        
        return {"stations": stations, "count": len(stations)}
        
    finally:
        await db_manager.disconnect()

@app.get("/api/sports")
async def get_sports():
    """스포츠 카테고리 목록 조회"""
    db_manager = DatabaseManager()
    await db_manager.connect()
    
    try:
        query = "SELECT sport_name, category_code FROM sports ORDER BY sport_name"
        result = await db_manager.execute_query(query)
        
        sports = []
        for row in result:
            sports.append({
                "name": row[0],
                "code": row[1]
            })
        
        return {"sports": sports, "count": len(sports)}
        
    finally:
        await db_manager.disconnect()

@app.get("/api/regions")
async def get_regions():
    """지역 목록 조회"""
    db_manager = DatabaseManager()
    await db_manager.connect()
    
    try:
        query = "SELECT ldong_regn_cd, ldong_regn_nm, ldong_sigungu_cd, ldong_sigungu_nm FROM region ORDER BY ldong_regn_nm, ldong_sigungu_nm"
        result = await db_manager.execute_query(query)
        
        regions = []
        for row in result:
            regions.append({
                "area_code": row[0],
                "area_name": row[1],
                "sigungu_code": row[2],
                "sigungu_name": row[3]
            })
        
        return {"regions": regions, "count": len(regions)}
        
    finally:
        await db_manager.disconnect()

#=============================================================================
# ✅ 데이터 동기화 API (관리자 / 스케줄러 용도)
#=============================================================================



@app.post("/api/sync/regions-from-api")
async def sync_regions_from_api(
    num_of_rows: int = Query(1000, description="가져올 최대 지역 수")
):
    """지역 데이터 동기화"""
    db_manager = DatabaseManager()
    await db_manager.connect()
    
    try:
        service = SyncRegionService(db_manager)
        return await service.sync_regions_from_api(num_of_rows)
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



