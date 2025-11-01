from app.services.sync_observation import (
    sync_surface_observations,  # 지상관측값 동기화
    sync_buoy_observations,     # 해양관측값 동기화
    sync_all_observations       # 통합 (지상+해양) 관측값 동기화
)

from fastapi import APIRouter

router = APIRouter(prefix="/observation", tags=["Observation Data"])

@router.post("/sync")
def sync_all_observations_api():
    """지상 + 해양 관측값 데이터를 통합하여 observation_data 테이블에 저장"""
    return sync_all_observations()

@router.post("/sync/surface")
def sync_surface_observations_api():
    """지상관측 데이터만 DB에 저장"""
    return sync_surface_observations()

@router.post("/sync/buoy")
def sync_buoy_observations_api():
    """해양관측 데이터만 DB에 저장"""
    return sync_buoy_observations()
