from typing import List, Dict, Any, Optional
import httpx
import asyncio
from urllib.parse import quote_plus
from ..manager import DatabaseManager
from ....config import TOURIST_API_KEY


class RegionRepository:
    """지역 관련 데이터베이스 작업"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    async def validate_sigungu_code(self, sigungu_code: str) -> bool:
        """시군구 코드가 region 테이블에 존재하는지 검증"""
        try:
            query = "SELECT COUNT(*) FROM region WHERE ldong_sigungu_cd = %s"
            result = await self.db.execute_query(query, (sigungu_code,))
            return result and result[0][0] > 0
        except Exception as e:
            print(f"❌ Failed to validate sigungu_code {sigungu_code}: {e}")
            return False
    

    async def fetch_regions_from_api(self, num_of_rows: int = 1000) -> List[Dict[str, Any]]:
        """한국관광공사 지역코드 API에서 지역 정보를 가져옴"""
        url = "https://apis.data.go.kr/B551011/KorService2/ldongCode2"
        
        params = {
            "serviceKey": quote_plus(TOURIST_API_KEY),
            "numOfRows": num_of_rows,
            "pageNo": 1,
            "MobileOS": "ETC",
            "MobileApp": "APP",
            "_type": "json",
            "lDongListYn": "Y"
        }
        
        try:
            print("🗺️ Fetching region data from Korean Tourism API...")
            print(f"🔑 Using API key: {TOURIST_API_KEY[:10]}...")
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=30.0)
                print(f"📡 Response status: {response.status_code}")
                print(f"📄 Response content length: {len(response.content)}")
                print(f"📝 Response content preview: {response.text[:200]}...")
                
                response.raise_for_status()
                
                # Check if response is empty
                if not response.text.strip():
                    print("❌ Empty response from API")
                    return []
                
                try:
                    data = response.json()
                except ValueError as json_error:
                    print(f"❌ JSON parsing error: {json_error}")
                    print(f"📄 Raw response: {response.text[:500]}")
                    return []
                
                if data.get("response", {}).get("header", {}).get("resultCode") != "0000":
                    print(f"❌ API error: {data.get('response', {}).get('header', {}).get('resultMsg', 'Unknown error')}")
                    return []
                
                items = data.get("response", {}).get("body", {}).get("items", {}).get("item", [])
                
                if not items:
                    print("⚠️ No region data found in API response")
                    return []
                
                regions = []
                for item in items:
                    regions.append({
                        "area_code": item.get("lDongRegnCd"),
                        "area_name": item.get("lDongRegnNm"),
                        "sigungu_code": item.get("lDongSignguCd"),
                        "sigungu_name": item.get("lDongSignguNm")
                    })
                
                print(f"✅ Successfully fetched {len(regions)} regions from API")
                return regions
                
        except httpx.TimeoutException:
            print("❌ API request timeout (30 seconds)")
            return []
        except httpx.HTTPStatusError as e:
            print(f"❌ HTTP error {e.response.status_code}: {e.response.text}")
            return []
        except httpx.RequestError as e:
            print(f"❌ Network error: {e}")
            return []
        except Exception as e:
            print(f"❌ Unexpected error fetching regions: {e}")
            return []

    async def sync_regions_from_api(self, num_of_rows: int = 1000) -> Dict[str, Any]:
        """API에서 지역 데이터를 가져와서 DB에 저장"""
        try:
            print("🗺️ Starting region data sync from API...")
            
            # API에서 지역 데이터 가져오기
            regions = await self.fetch_regions_from_api(num_of_rows)
            
            if not regions:
                return {"success": False, "message": "No region data fetched from API", "count": 0}
            
            # DB에 저장
            affected_rows = 0
            for region in regions:
                try:
                    area_code = region.get("area_code")
                    area_name = region.get("area_name")
                    sigungu_code = region.get("sigungu_code")
                    sigungu_name = region.get("sigungu_name")
                    
                    if not all([area_code, area_name, sigungu_code, sigungu_name]):
                        continue
                    
                    # UPSERT 쿼리 (기존 데이터가 있으면 업데이트, 없으면 삽입)
                    upsert_query = """
                        INSERT INTO region (ldong_regn_cd, ldong_regn_nm, ldong_sigungu_cd, ldong_sigungu_nm)
                        VALUES (%s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                        ldong_regn_nm = VALUES(ldong_regn_nm),
                        ldong_sigungu_nm = VALUES(ldong_sigungu_nm)
                    """
                    
                    cursor = self.db.connection.cursor()
                    cursor.execute(upsert_query, (area_code, area_name, sigungu_code, sigungu_name))
                    affected_rows += cursor.rowcount
                    cursor.close()
                    
                except Exception as e:
                    print(f"❌ Failed to upsert region {region}: {e}")
                    continue
            
            print(f"✅ Successfully synced {affected_rows} regions to database")
            
            return {
                "success": True,
                "message": f"Region data synced successfully from API",
                "fetched_count": len(regions),
                "affected_rows": affected_rows
            }
            
        except Exception as e:
            print(f"❌ Region data sync from API failed: {e}")
            return {"success": False, "message": str(e), "count": 0}