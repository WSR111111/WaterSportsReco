from fastapi import APIRouter, Depends
from app.services.sync_region import sync_region
from app.db.dependencies import get_db
from app.db.database import DatabaseManager

router = APIRouter()

# FastAPI의 엔드포인트
@router.post("/region/sync")
def sync_region_api():
    """TourAPI에서 지역코드를 가져와 DB에 저장"""
    result = sync_region()
    return result

# DB에서 지역 목록 불러오기
@router.get("/region/list")
def get_region(db: DatabaseManager = Depends(get_db)):
    query = "SELECT region_id, lDongRegnCd, lDongSignguCd, lDongRegnNm, lDongSignguNm FROM region"
    region = db.execute_query(query)
    return [
        {
            "region_id": r[0],
            "lDongRegnCd": r[1],
            "lDongSignguCd": r[2],
            "lDongRegnNm": r[3],
            "lDongSignguNm": r[4]
        }
        for r in region
    ]