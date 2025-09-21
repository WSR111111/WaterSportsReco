import asyncio
import httpx
from typing import Dict, Any, Optional
from ..clients.kma.marine_client import fetch_all_marine_stations
from ..db.manager import DatabaseManager
from ..db.repositories.station_repository import StationRepository


class SyncMarineService:
    """해양 관측 데이터 동기화 서비스"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.station_repo = StationRepository(db_manager)
        self.http_client = None
    
    async def __aenter__(self):
        """비동기 컨텍스트 매니저 진입"""
        self.http_client = httpx.AsyncClient(timeout=120.0)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """비동기 컨텍스트 매니저 종료"""
        if self.http_client:
            await self.http_client.aclose()
    
    async def sync_marine_data(self, tm: Optional[str] = None) -> Dict[str, Any]:
        """해양 관측소 데이터 동기화"""
        try:
            print("🌊 Starting marine data sync...")
            
            # 해양 관측 데이터 가져오기 (관측소 정보 포함)
            stations = await fetch_all_marine_stations(self.http_client, tm)
            
            if not stations:
                return {"success": False, "message": "No marine data fetched", "count": 0}
            
            affected_rows = await self.station_repo.upsert_ocean_info(stations)
            
            return {
                "success": True,
                "message": f"Marine data synced successfully",
                "fetched_count": len(stations),
                "affected_rows": affected_rows,
                "station_count": 0
            }
            
        except Exception as e:
            print(f"❌ Marine data sync failed: {e}")
            return {"success": False, "message": str(e), "count": 0}