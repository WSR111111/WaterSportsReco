from app.services.sync_leisure import (
    sync_leisure_places,  # 레저시설 목록 동기화
    sync_place_details    # 각 시설 상세정보 동기화
)

from fastapi import APIRouter

router = APIRouter(prefix="/leisure", tags=["Leisure"])

@router.post("/sync")
def sync_leisure_places_api():
    """TourAPI에서 레저스포츠 시설 목록을 수집해 DB에 저장"""
    return sync_leisure_places()

@router.post("/sync/details")
def sync_leisure_details_api():
    """DB에 저장된 content_id 기준으로 상세정보를 동기화"""
    return sync_place_details()
