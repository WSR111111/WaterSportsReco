from fastapi import APIRouter
from app.services.sync_leisure import sync_leisure_places, sync_place_details

router = APIRouter()

@router.post("/leisure/sync/places")
def sync_leisure_places_api(area_code: str = None, sigungu_code: str = None, num_rows: int = 1000):
    """레저스포츠 사업장 목록 동기화 (전체 데이터 수집)"""
    return sync_leisure_places(area_code, sigungu_code, num_rows)

@router.post("/leisure/sync/details")
def sync_place_details_api():
    """사업장 상세정보 동기화 (leisure_place에 있는 content_id 기준)"""
    return sync_place_details()
