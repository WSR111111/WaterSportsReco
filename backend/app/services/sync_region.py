from app.utils.tourapi_client import fetch_region
from app.db.database import DatabaseManager

def sync_region(area_code: str = None):
    """
    TourAPI에서 지역코드(lDongRegnCd, lDongSignguCd 등) 불러와 region 테이블 저장
    """
    # 네트워크 연결 테스트
    import requests
    try:
        print("네트워크 연결 테스트 중...")
        test_response = requests.get("https://www.google.com", timeout=10)
        print(f"Google 연결 성공: {test_response.status_code}")
    except Exception as e:
        print(f"네트워크 연결 실패: {e}")
        return {"status": "fail", "message": f"네트워크 연결 문제: {e}"}
    
    db = DatabaseManager()
    if not db.connect():
        return {"status": "fail", "message": "DB 연결 실패"}

    try:
        print("지역 API 호출 시작...")
        data = fetch_region(area_code)
        print(f"API 응답 받음: {data}")
        
        items = data["response"]["body"]["items"]["item"]

        for item in items:
            query = """
            INSERT INTO region (lDongRegnCd, lDongSignguCd, lDongRegnNm, lDongSignguNm)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                lDongRegnNm = VALUES(lDongRegnNm),
                lDongSignguNm = VALUES(lDongSignguNm)
            """
            db.execute_non_query(query, (
                item.get("lDongRegnCd"),    # 광역시/도 코드
                item.get("lDongSignguCd"),  # 시군구 코드
                item.get("lDongRegnNm"),    # 광역시/도 이름
                item.get("lDongSignguNm")   # 시군구 이름
            ))

        return {"status": "success", "count": len(items)}

    except Exception as e:
        return {"status": "fail", "message": str(e)}

    finally:
        db.disconnect()