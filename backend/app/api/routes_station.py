from fastapi import APIRouter
from app.services.sync_station import sync_surface_stations, sync_buoy_stations

router = APIRouter()

@router.post("/station/sync/surface")
def sync_surface_stations_api(tm: str = None, debug: bool = False):
    """지상 관측소 DB 저장 (tm 생략시 현재시간 사용)"""
    return sync_surface_stations(tm, debug)

@router.post("/station/sync/buoy")
def sync_buoy_stations_api(tm: str = None, debug: bool = False):
    """해양 관측소 DB 저장 (tm 생략시 현재시간 사용)"""
    return sync_buoy_stations(tm, debug)
