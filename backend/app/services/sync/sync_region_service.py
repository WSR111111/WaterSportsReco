from typing import Dict, Any, List
from ..db.manager import DatabaseManager
from ..db.repositories.region_repository import RegionRepository


class SyncRegionService:
    """지역 데이터 동기화 서비스"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.region_repo = RegionRepository(db_manager)
    
    async def sync_regions_from_codes(self, region_codes: List[Dict[str, str]]) -> Dict[str, Any]:
        """지역 코드 목록으로부터 지역 데이터 동기화"""
        try:
            print("🗺️ Starting region data sync...")
            
            if not region_codes:
                return {"success": False, "message": "No region codes provided", "count": 0}
            
            created_count = 0
            for region_code in region_codes:
                sigungu_code = region_code.get('sigungu_code')
                area_code = region_code.get('area_code')
                
                if not sigungu_code:
                    continue
                
                if await self.region_repo.ensure_region_exists_by_sigungu(sigungu_code, area_code):
                    created_count += 1
            
            return {
                "success": True,
                "message": f"Region data synced successfully",
                "processed_count": len(region_codes),
                "created_count": created_count
            }
            
        except Exception as e:
            print(f"❌ Region data sync failed: {e}")
            return {"success": False, "message": str(e), "count": 0}
    
    async def validate_region_codes(self, sigungu_codes: List[str]) -> Dict[str, bool]:
        """여러 시군구 코드의 유효성을 일괄 검증"""
        results = {}
        for code in sigungu_codes:
            results[code] = await self.region_repo.validate_sigungu_code(code)
        return results