"""
app/api/station_router.py
────────────────────────────────────────────
- 지상/해양 관측소 + 단기/중기 예보 구역정보 동기화 라우터
"""
from fastapi import APIRouter, Query
from app.services.sync_station import (
    sync_surface_stations,  # 지상관측소 동기화
    sync_buoy_stations,     # 해양관측소 동기화
    sync_all_stations       # 통합 (지상+해양) 동기화
)
from app.services.sync_forecast_station import (
    sync_short_term_stations,  # 단기예보 구역정보 동기화
    sync_medium_term_stations  # 중기예보 구역정보 동기화
)

router = APIRouter(prefix="/station", tags=["Observation Station"])


# =========================================================
# 🌎 실측 관측소 (지상 + 해양)
# =========================================================
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


# =========================================================
# ☁️ 예보 구역정보 (단기 + 중기)
# =========================================================
@router.post("/sync/forecast/short")
def sync_short_term_stations_api(debug: bool = Query(False, description="디버그 모드")):
    """단기예보 구역정보 수집 및 DB 저장"""
    return sync_short_term_stations(debug)


@router.post("/sync/forecast/medium")
def sync_medium_term_stations_api(debug: bool = Query(False, description="디버그 모드")):
    """중기예보 구역정보 수집 및 DB 저장"""
    return sync_medium_term_stations(debug)


@router.post("/sync/forecast/all")
def sync_all_forecast_stations_api(debug: bool = Query(False, description="디버그 모드")):
    """단기 + 중기 예보 구역정보를 한 번에 동기화"""
    short_result = sync_short_term_stations(debug)
    medium_result = sync_medium_term_stations(debug)
    return {
        "message": "단기 + 중기 예보 구역정보 동기화 완료",
        "result": {
            "short_term": short_result,
            "medium_term": medium_result
        }
    }
