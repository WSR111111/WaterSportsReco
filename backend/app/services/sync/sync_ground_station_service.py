import httpx
from typing import Dict, Any, Optional
from ..clients.kma.kma_surface_client import fetch_surface_station_info
from ..db.manager import DatabaseManager
from ..db.repositories.station_repository import StationRepository


class SyncGroundStationService:
    """지상 관측소 정보 동기화 서비스 (관측소 정보만)"""
    
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
    
    async def sync_ground_stations_data(self, tm: Optional[str] = None) -> Dict[str, Any]:
        """지상 관측소 정보만 동기화 (관측 데이터 제외)"""
        try:
            print("📍 Starting ground stations info sync...")
            
            # 지상 관측소 정보 가져오기
            stations_info = await fetch_surface_station_info(self.http_client, tm)
            
            if not stations_info:
                return {"success": False, "message": "No ground station info fetched", "count": 0}
            
            # 관측소 정보만 저장
            print(f"📍 Syncing {len(stations_info)} ground station info...")
            affected_rows = await self.station_repo.upsert_ground_stations(stations_info)
            
            return {
                "success": True,
                "message": f"Ground stations info synced successfully",
                "fetched_count": len(stations_info),
                "affected_rows": affected_rows
            }
            
        except Exception as e:
            print(f"❌ Ground stations info sync failed: {e}")
            return {"success": False, "message": str(e), "count": 0}