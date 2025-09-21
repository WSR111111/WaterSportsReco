import httpx
from typing import Dict, Any, Optional
from ..clients.tourist_client import fetch_leisure_places_json
from ..db.manager import DatabaseManager
from ..db.repositories.place_repository import PlaceRepository
from ..db.repositories.region_repository import RegionRepository
from ..db.repositories.sports_repository import SportsRepository


class SyncLeisureService:
    """레저 장소 데이터 동기화 서비스"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.place_repo = PlaceRepository(db_manager)
        self.region_repo = RegionRepository(db_manager)
        self.sports_repo = SportsRepository(db_manager)
        self.http_client = None
    
    async def __aenter__(self):
        """비동기 컨텍스트 매니저 진입"""
        self.http_client = httpx.AsyncClient(timeout=120.0)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """비동기 컨텍스트 매니저 종료"""
        if self.http_client:
            await self.http_client.aclose()
    
    async def sync_leisure_places_data(self, area_code: Optional[str] = None, 
                                     sigungu_code: Optional[str] = None,
                                     num_of_rows: int = 1000) -> Dict[str, Any]:
        """레저 장소 데이터 동기화 (JSON API 사용)"""
        try:
            print("🏄 Starting leisure places data sync...")
            
            leisure_places = await fetch_leisure_places_json(
                client=self.http_client,
                area_code=area_code,
                sigungu_code=sigungu_code,
                content_type_id="28",  # 레포츠
                cat1="A03",           # 레저스포츠
                cat2="A0303",         # 수상레저스포츠
                num_of_rows=num_of_rows,
                arrange="C"           # 수정일 순
            )
            
            print(f"🔍 Fetched {len(leisure_places)} leisure places from API")
            
            if not leisure_places:
                return {"success": False, "message": "No leisure places data fetched", "count": 0}
            
            affected_rows = await self.place_repo.upsert_leisure_places(
                leisure_places, self.region_repo, self.sports_repo
            )
            
            return {
                "success": True,
                "message": f"Leisure places data synced successfully",
                "fetched_count": len(leisure_places),
                "affected_rows": affected_rows
            }
            
        except Exception as e:
            print(f"❌ Leisure places data sync failed: {e}")
            return {"success": False, "message": str(e), "count": 0}