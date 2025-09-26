from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List
from app.services.sync_leisure import sync_leisure_places, sync_place_details
from app.db.database import DatabaseManager

router = APIRouter()

# 동기화 API
@router.post("/leisure/sync/places")
def sync_leisure_places_api(area_code: str = None, sigungu_code: str = None, num_rows: int = 1000):
    """레저스포츠 사업장 목록 동기화 (전체 데이터 수집)"""
    return sync_leisure_places(area_code, sigungu_code, num_rows)

@router.post("/leisure/sync/details")
def sync_place_details_api():
    """사업장 상세정보 동기화 (leisure_place에 있는 content_id 기준)"""
    return sync_place_details()

# DB에서 수상 스포츠 목록 조회하기
@router.get("/leisure/map/places")
def get_map_places(
    category_code: Optional[str] = Query(None, description="스포츠 카테고리 코드"),
    area_code: Optional[str] = Query(None, description="지역 코드 (lDongRegnCd)")
):
    """지도에 표시할 레저스포츠 장소 목록 조회 (좌표 있는 것만)"""
    db = DatabaseManager()
    if not db.connect():
        raise HTTPException(status_code=500, detail="DB 연결 실패")
    
    try:
        # 좌표가 있는 데이터만 조회 (지도 표시용)
        query = """
        SELECT lp.content_id, lp.category_code, lp.place_name, lp.address, 
               lp.latitude, lp.longitude, lp.first_image, s.sport_name, lp.lDongRegnCd
        FROM leisure_place lp
        LEFT JOIN sports s ON lp.category_code = s.category_code
        WHERE lp.latitude IS NOT NULL AND lp.longitude IS NOT NULL
        """
        params = []
        
        # 카테고리 필터
        if category_code:
            query += " AND lp.category_code = %s"
            params.append(category_code)
        
        # 지역 필터 (lDongRegnCd 사용)
        if area_code:
            query += " AND lp.lDongRegnCd = %s"
            params.append(area_code)
        
        query += " ORDER BY lp.place_name"
        
        results = db.execute_query(query, params)
        
        places = []
        for row in results:
            places.append({
                "content_id": row[0],
                "category_code": row[1],
                "place_name": row[2],
                "address": row[3],
                "latitude": float(row[4]),
                "longitude": float(row[5]),
                "first_image": row[6],
                "sport_name": row[7],
                "area_code": row[8]
            })
        
        return {"places": places, "count": len(places)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.disconnect()

# 특정 장소의 상세 정보 조회
@router.get("/leisure/place/{content_id}")
def get_place_detail(content_id: str):
    """특정 레저스포츠 장소의 상세 정보 조회"""
    db = DatabaseManager()
    if not db.connect():
        raise HTTPException(status_code=500, detail="DB 연결 실패")
    
    try:
        # 기본 장소 정보와 상세 정보를 조인해서 조회
        query = """
        SELECT lp.content_id, lp.category_code, lp.place_name, lp.address, lp.address2,
               lp.phone_number, lp.latitude, lp.longitude, lp.first_image, lp.first_image2,
               lp.lDongRegnCd, lp.lDongSignguCd, s.sport_name,
               pd.homepage, pd.overview,
               r.lDongRegnNm, r.lDongSignguNm
        FROM leisure_place lp
        LEFT JOIN place_detail pd ON lp.content_id = pd.content_id
        LEFT JOIN sports s ON lp.category_code = s.category_code
        LEFT JOIN region r ON lp.lDongSignguCd = r.lDongSignguCd
        WHERE lp.content_id = %s
        """
        
        results = db.execute_query(query, [content_id])
        
        if not results:
            raise HTTPException(status_code=404, detail="해당 장소를 찾을 수 없습니다")
        
        row = results[0]
        place_detail = {
            "content_id": row[0],
            "category_code": row[1],
            "place_name": row[2],
            "address": row[3],
            "address2": row[4],
            "phone_number": row[5],
            "latitude": float(row[6]) if row[6] else None,
            "longitude": float(row[7]) if row[7] else None,
            "first_image": row[8],
            "first_image2": row[9],
            "area_code": row[10],
            "sigungu_code": row[11],
            "sport_name": row[12],
            "homepage": row[13],
            "overview": row[14],
            "region_name": row[15],
            "sigungu_name": row[16]
        }
        
        return place_detail
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.disconnect()
