from app.services.sync_code import (
    sync_code_from_csv,   # CSV 기반 코드 동기화 (선택)
    sync_all_codes        # 지역 + 스포츠 전체 동기화 (최종)
)

from fastapi import APIRouter

router = APIRouter(prefix="/code", tags=["Code Table"])

@router.post("/sync")
def sync_all_codes_api():
    """TourAPI 지역 + 스포츠 카테고리를 code 테이블에 동기화"""
    return sync_all_codes()

@router.post("/sync/region")
def sync_region_api():
    """TourAPI에서 지역 코드 데이터를 code 테이블에 저장"""
    return sync_region_from_api()

@router.post("/sync/sports")
def sync_sports_api():
    """TourAPI에서 스포츠 카테고리 코드를 code 테이블에 저장"""
    return sync_sports_from_api()
