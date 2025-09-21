from typing import Dict, Any, List
from ..db.manager import DatabaseManager
from ..db.repositories.region_repository import RegionRepository


class SyncRegionService:
    """지역 데이터 동기화 서비스"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.region_repo = RegionRepository(db_manager)
    

    async def sync_regions_from_api(self, num_of_rows: int = 1000) -> Dict[str, Any]:
        """지역 데이터 동기화"""
        try:
            print("🗺️ Starting region data sync from API...")
            
            result = await self.region_repo.sync_regions_from_api(num_of_rows)
            
            return result
            
        except Exception as e:
            print(f"❌ Region data sync from API failed: {e}")
            return {"success": False, "message": str(e), "count": 0}
    
    async def validate_region_codes(self, sigungu_codes: List[str]) -> Dict[str, bool]:
        """여러 시군구 코드의 유효성을 일괄 검증"""
        results = {}
        for code in sigungu_codes:
            results[code] = await self.region_repo.validate_sigungu_code(code)
        return results