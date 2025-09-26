from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from app.services.sync_observation import sync_surface_observations, sync_buoy_observations
from app.db.database import DatabaseManager

router = APIRouter()

@router.post("/observation/sync/surface")
def sync_surface(tm: str = None, debug: bool = False):
    """지상관측값 DB 저장 (tm 생략시 현재시간 사용, 모든 관측소 데이터)"""
    return sync_surface_observations(tm, "0", debug)

@router.post("/observation/sync/buoy")
def sync_buoy(tm: str = None, debug: bool = False):
    """해양관측값 DB 저장 (tm 생략시 현재시간 사용, 모든 관측소 데이터)"""
    return sync_buoy_observations(tm, "0", debug)


# DB에서 해양 관측 정보 조회
@router.get("/observation/marine")
def get_marine_observations(
    station_id: Optional[str] = Query(None, description="특정 관측소 ID")
):
    """해양 관측 데이터 조회"""
    db = DatabaseManager()
    if not db.connect():
        raise HTTPException(status_code=500, detail="DB 연결 실패")
    
    try:
        # 해양 관측소의 최신 관측 데이터를 피벗 형태로 조회
        query = """
        SELECT 
            s.station_id,
            s.station_nm,
            s.lat,
            s.lon,
            MAX(CASE WHEN od.observation_cd = 'TW' THEN od.observation_value END) as sst,
            MAX(CASE WHEN od.observation_cd = 'WH_SIG' THEN od.observation_value END) as wave_height,
            MAX(CASE WHEN od.observation_cd = 'WD' THEN od.observation_value END) as wave_direction,
            MAX(CASE WHEN od.observation_cd = 'WP' THEN od.observation_value END) as wave_period,
            MAX(CASE WHEN od.observation_cd = 'WS' THEN od.observation_value END) as wind_speed,
            MAX(CASE WHEN od.observation_cd = 'TA' THEN od.observation_value END) as temperature,
            MAX(od.observed_at) as observed_at
        FROM station s
        LEFT JOIN observation_data od ON s.station_id = od.station_id
        WHERE s.category = 'MARINE'
        """
        params = []
        
        # 특정 관측소 필터
        if station_id:
            query += " AND s.station_id = %s"
            params.append(station_id)
        
        query += """
        GROUP BY s.station_id, s.station_nm, s.lat, s.lon
        HAVING MAX(od.observed_at) IS NOT NULL
        ORDER BY observed_at DESC
        """
        
        results = db.execute_query(query, params)
        
        observations = []
        for row in results:
            observations.append({
                "station_id": row[0],
                "station_name": row[1],
                "lat": float(row[2]) if row[2] else None,
                "lon": float(row[3]) if row[3] else None,
                "sst": float(row[4]) if row[4] is not None else None,
                "wave_height": float(row[5]) if row[5] is not None else None,
                "wave_direction": float(row[6]) if row[6] is not None else None,
                "wave_period": float(row[7]) if row[7] is not None else None,
                "wind_speed": float(row[8]) if row[8] is not None else None,
                "temperature": float(row[9]) if row[9] is not None else None,
                "observed_at": str(row[10]) if row[10] else None
            })
        
        return {"stations": observations, "count": len(observations)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.disconnect()


# DB에서 지상 관측 정보 조회
@router.get("/observation/surface")
def get_surface_observations(
    station_id: Optional[str] = Query(None, description="특정 관측소 ID")
):
    """지상 관측 데이터 조회"""
    db = DatabaseManager()
    if not db.connect():
        raise HTTPException(status_code=500, detail="DB 연결 실패")
    
    try:
        # 지상 관측소의 최신 관측 데이터를 피벗 형태로 조회
        query = """
        SELECT 
            s.station_id,
            s.station_nm,
            s.lat,
            s.lon,
            MAX(CASE WHEN od.observation_cd = 'TA' THEN od.observation_value END) as temperature,
            MAX(CASE WHEN od.observation_cd = 'HM' THEN od.observation_value END) as humidity,
            MAX(CASE WHEN od.observation_cd = 'WS' THEN od.observation_value END) as wind_speed,
            MAX(CASE WHEN od.observation_cd = 'WD' THEN od.observation_value END) as wind_direction,
            MAX(CASE WHEN od.observation_cd = 'PA' THEN od.observation_value END) as pressure,
            MAX(CASE WHEN od.observation_cd = 'RN' THEN od.observation_value END) as precipitation,
            MAX(od.observed_at) as observed_at
        FROM station s
        LEFT JOIN observation_data od ON s.station_id = od.station_id
        WHERE s.category = 'SURFACE'
        """
        params = []
        
        # 특정 관측소 필터
        if station_id:
            query += " AND s.station_id = %s"
            params.append(station_id)
        
        query += """
        GROUP BY s.station_id, s.station_nm, s.lat, s.lon
        HAVING MAX(od.observed_at) IS NOT NULL
        ORDER BY observed_at DESC
        """
        
        results = db.execute_query(query, params)
        
        observations = []
        for row in results:
            observations.append({
                "station_id": row[0],
                "station_name": row[1],
                "lat": float(row[2]) if row[2] else None,
                "lon": float(row[3]) if row[3] else None,
                "temperature": float(row[4]) if row[4] is not None else None,
                "humidity": float(row[5]) if row[5] is not None else None,
                "wind_speed": float(row[6]) if row[6] is not None else None,
                "wind_direction": float(row[7]) if row[7] is not None else None,
                "pressure": float(row[8]) if row[8] is not None else None,
                "precipitation": float(row[9]) if row[9] is not None else None,
                "observed_at": str(row[10]) if row[10] else None
            })
        
        return {"stations": observations, "count": len(observations)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.disconnect()


# 관측소 목록 조회 (좌표 정보 포함)
@router.get("/observation/stations")
def get_observation_stations(
    category: Optional[str] = Query(None, description="관측소 카테고리 (MARINE, SURFACE)")
):
    """관측소 목록 조회"""
    db = DatabaseManager()
    if not db.connect():
        raise HTTPException(status_code=500, detail="DB 연결 실패")
    
    try:
        query = """
        SELECT station_id, station_nm, lat, lon, category
        FROM station
        WHERE lat IS NOT NULL AND lon IS NOT NULL
        """
        params = []
        
        # 카테고리 필터
        if category:
            query += " AND category = %s"
            params.append(category)
        
        query += " ORDER BY station_nm"
        
        results = db.execute_query(query, params)
        
        stations = []
        for row in results:
            stations.append({
                "station_id": row[0],
                "station_name": row[1],
                "lat": float(row[2]) if row[2] else None,
                "lon": float(row[3]) if row[3] else None,
                "category": row[4]
            })
        
        return {"stations": stations, "count": len(stations)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.disconnect()
