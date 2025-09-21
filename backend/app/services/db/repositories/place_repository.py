from typing import List, Dict, Any
from ..manager import DatabaseManager


class PlaceRepository:
    """장소 관련 데이터베이스 작업"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    async def upsert_leisure_places(self, spots: List[Dict[str, Any]], region_repo, sports_repo) -> int:
        """관광지 데이터를 leisure_place와 place_detail 테이블에 upsert"""
        if not spots:
            return 0
        
        affected_rows = 0
        for spot in spots:
            try:
                lat = spot.get('mapy')
                lon = spot.get('mapx')
                title = spot.get('title', 'Unknown')
                
                if lat is None or lon is None:
                    continue
                
                # sigungu_code 검증 (필수 필드)
                sigungu_code = spot.get('sigungucode', '')
                if not sigungu_code:
                    print(f"⚠️ Skipping leisure place {title}: missing sigungu_code")
                    continue
                
                # cat3 검증 (외래키 제약조건)
                cat3 = spot.get('cat3', '')
                if not cat3:
                    print(f"⚠️ Skipping leisure place {title}: missing cat3")
                    continue
                
                # 외래키 제약조건 검증 (region이 존재하는지 확인만)
                area_code = spot.get('areacode', '')
                if not await region_repo.validate_sigungu_code(sigungu_code):
                    print(f"⚠️ Skipping leisure place {title}: region not found for sigungu_code {sigungu_code}")
                    continue
                
                if not await sports_repo.ensure_sport_exists_by_cat3(cat3):
                    print(f"⚠️ Skipping leisure place {title}: failed to ensure sport exists for cat3 {cat3}")
                    continue
                
                # 새로운 테이블 스키마에 맞춘 INSERT 문
                leisure_upsert_sql = """
                    INSERT INTO leisure_place 
                    (cat3, content_id, place_name, address, address2, 
                     phone_number, latitude, longitude, area_code, sigungu_code,
                     first_image, first_image2)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    cat3 = VALUES(cat3),
                    place_name = VALUES(place_name),
                    address = VALUES(address),
                    address2 = VALUES(address2),
                    phone_number = VALUES(phone_number),
                    latitude = VALUES(latitude),
                    longitude = VALUES(longitude),
                    area_code = VALUES(area_code),
                    sigungu_code = VALUES(sigungu_code),
                    first_image = VALUES(first_image),
                    first_image2 = VALUES(first_image2)
                """
                cursor = self.db.connection.cursor() 
                cursor.execute(leisure_upsert_sql, (
                    cat3,
                    spot.get('content_id', ''),
                    title,
                    spot.get('addr1', ''),
                    spot.get('addr2', ''),
                    spot.get('tel', ''),
                    lat,
                    lon,
                    spot.get('areacode', ''),
                    sigungu_code,
                    spot.get('firstimage', ''),
                    spot.get('firstimage2', '')
                ))
                
                affected_rows += cursor.rowcount
                cursor.close()
                
            except Exception as e:
                print(f"❌ Failed to upsert leisure place for {spot.get('title')}: {e}")
                # 외래키 제약조건 위반 등의 상세 에러 로깅
                if "foreign key constraint" in str(e).lower():
                    print(f"   🔗 Foreign key constraint violation - sigungu_code: {spot.get('sigungucode')}, cat3: {spot.get('cat3')}")
                continue
        
        print(f"✅ Upserted {affected_rows} leisure places")
        return affected_rows
    
    async def upsert_place_details(self, details: List[Dict[str, Any]]) -> int:
        """장소 상세정보를 place_detail 테이블에 upsert"""
        if not details:
            return 0
        
        affected_rows = 0
        for detail in details:
            try:
                content_id = detail.get('contentid', '')
                homepage = detail.get('homepage', '')
                overview = detail.get('overview', '')
                
                if not content_id:
                    print(f"⚠️ Skipping detail with missing content_id: {detail}")
                    continue
                
                upsert_sql = """
                    INSERT INTO place_detail (content_id, homepage, overview)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    homepage = VALUES(homepage),
                    overview = VALUES(overview)
                """
                cursor = self.db.connection.cursor()
                cursor.execute(upsert_sql, (content_id, homepage, overview))
                affected_rows += cursor.rowcount
                cursor.close()
                
            except Exception as e:
                print(f"❌ Failed to upsert detail for content_id {detail.get('contentid', 'Unknown')}: {e}")
                continue
        
        print(f"✅ Upserted {affected_rows} place details")
        return affected_rows