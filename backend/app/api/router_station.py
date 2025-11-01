from app.services.sync_station import (
    sync_surface_stations,  # 지상관측소 동기화
    sync_buoy_stations,     # 해양관측소 동기화
    sync_all_stations       # 통합 (지상+해양) 동기화
)

from fastapi import APIRouter

router = APIRouter(prefix="/station", tags=["Observation Station"])

@router.post("/sync")
def sync_all_stations_api():
    """지상 + 해양 관측소 전체를 observation_station 테이블에 저장"""
    return sync_all_stations()

@router.post("/sync/surface")
def sync_surface_stations_api():
    """지상관측소 데이터만 동기화"""
    return sync_surface_stations()

@router.post("/sync/buoy")
def sync_buoy_stations_api():
    """해양관측소 데이터만 동기화"""
    return sync_buoy_stations()
