from fastapi import APIRouter, Depends
from app.services.sync_sports import sync_sports
from app.db.dependencies import get_db
from app.db.database import DatabaseManager

router = APIRouter()

@router.post("/sports/sync")
def sync_sports_api(cat1: str = "A03", cat2: str = "A0303"):
    """
    TourAPI 스포츠 카테고리 → DB 저장
    기본값: 레저스포츠(A03) > 수상레저스포츠(A0303)
    """
    return sync_sports(cat1=cat1, cat2=cat2)


# DB에서 수상스포츠 목록 불러오기
@router.get("/sports/list")
def get_sports(db: DatabaseManager = Depends(get_db)):
    query = "SELECT sport_id, category_code, sport_name FROM sports"
    sports = db.execute_query(query)
    return [
        {
            "sport_id": r[0],
            "category_code": r[1],
            "sport_name": r[2],
        }
        for r in sports
    ]
