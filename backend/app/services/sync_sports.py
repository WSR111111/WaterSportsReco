from app.utils.tourapi_client import fetch_sports
from app.db.database import DatabaseManager

def sync_sports(cat1: str = "A03", cat2: str = "A0303"):
    """
    TourAPI에서 스포츠 카테고리 불러와 sports 테이블 저장
    - cat1="A03": 레저스포츠
    - cat2="A0303": 수상레저스포츠
    - 모든 cat3 세부 카테고리를 조회
    """
    db = DatabaseManager()
    if not db.connect():
        return {"status": "fail", "message": "DB 연결 실패"}

    try:
        data = fetch_sports(cat1=cat1, cat2=cat2)
        items = data["response"]["body"]["items"]["item"]

        count = 0
        for item in items:
            category_code = item.get("code")
            sport_name = item.get("name")

            if not category_code or not sport_name:
                continue

            query = """
            INSERT INTO sports (category_code, sport_name)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE
                sport_name = VALUES(sport_name)
            """
            db.execute_non_query(query, (category_code, sport_name))
            count += 1

        return {"status": "success", "count": count}

    except Exception as e:
        return {"status": "fail", "message": str(e)}

    finally:
        db.disconnect()
