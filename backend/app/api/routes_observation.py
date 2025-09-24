from fastapi import APIRouter
from app.services.sync_observation import sync_surface_observations, sync_buoy_observations

router = APIRouter()

@router.post("/observation/sync/surface")
def sync_surface(tm: str = None, debug: bool = False):
    """지상관측값 DB 저장 (tm 생략시 현재시간 사용, 모든 관측소 데이터)"""
    return sync_surface_observations(tm, "0", debug)

@router.post("/observation/sync/buoy")
def sync_buoy(tm: str = None, debug: bool = False):
    """해양관측값 DB 저장 (tm 생략시 현재시간 사용, 모든 관측소 데이터)"""
    return sync_buoy_observations(tm, "0", debug)
