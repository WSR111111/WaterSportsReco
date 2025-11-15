"""
app/api/observation_router.py
────────────────────────────────────────────
- 지상/해양 실측 관측값 + 단기/중기 예보 관측값 동기화 라우터
"""
from fastapi import APIRouter, Query
from app.services.sync_observation import (
    sync_surface_observations,  # 지상관측값 동기화
    sync_buoy_observations,     # 해양관측값 동기화
    sync_all_observations       # 통합 (지상+해양) 관측값 동기화
)
from app.services.sync_forecast_observation import (
    sync_short_term_forecast,   # 단기 예보 관측값 동기화
    sync_medium_term_forecast,  # 중기 예보 관측값 동기화
    sync_all_forecast           # 단기 + 중기 예보 관측값 통합 동기화
)

router = APIRouter(prefix="/observation", tags=["Observation Data"])


# =========================================================
# 🌎 실측 관측값 (지상 + 해양)
# =========================================================
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


# =========================================================
# ☁️ 예보 관측값 (단기 + 중기)
# =========================================================
@router.post("/sync/forecast/short")
def sync_short_term_forecast_api(debug: bool = Query(False, description="디버그 모드")):
    """단기예보(육상+해상) 관측값을 CSV 및 observation_data_short 테이블에 저장"""
    return sync_short_term_forecast(debug)


@router.post("/sync/forecast/medium")
def sync_medium_term_forecast_api(debug: bool = Query(False, description="디버그 모드")):
    """중기예보(육상+해상) 관측값을 CSV 및 observation_data_medium 테이블에 저장"""
    return sync_medium_term_forecast(debug)


@router.post("/sync/forecast/all")
def sync_all_forecast_observations_api(debug: bool = Query(False, description="디버그 모드")):
    """단기 + 중기 예보 관측값 전체를 한 번에 동기화"""
    result = sync_all_forecast(debug)
    return {
        "message": "단기 + 중기 예보 관측값 동기화 완료",
        "result": result
    }
