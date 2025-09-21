import asyncio
import httpx
from typing import Dict, Any, Optional
from ..clients.kma.kma_surface_client import fetch_surface_station_info, fetch_surface_obs
from ..db.manager import DatabaseManager
from ..db.repositories.station_repository import StationRepository


class SyncSurfaceService:
    """지상 관측 데이터 동기화 서비스"""
    
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
    
    async def sync_surface_data(self, tm: Optional[str] = None) -> Dict[str, Any]:
        """지상 관측소 데이터 동기화"""
        try:
            print("🌤️ Starting surface data sync...")
            
            # 관측소 정보와 실시간 관측 데이터를 병렬로 가져오기
            stations_info, observations = await asyncio.gather(
                fetch_surface_station_info(self.http_client, tm),
                fetch_surface_obs(self.http_client, tm1=tm)
            )
            
            if not stations_info:
                return {"success": False, "message": "No surface station info fetched", "count": 0}
            
            # 1. 먼저 관측소 정보 저장
            print(f"📍 Syncing {len(stations_info)} ground station info...")
            station_rows = await self.station_repo.upsert_ground_stations(stations_info)
            print(f"✅ Upserted {station_rows} ground stations")
            
            # 2. 관측 데이터를 station_id로 매핑
            obs_dict = {obs["station_id"]: obs for obs in observations}
            
            # 3. 관측소 정보와 관측 데이터 결합
            combined_stations = []
            for station in stations_info:
                station_id = station["stnid"]  # 지상관측소 정보에서는 stnid 사용
                combined_station = station.copy()
                combined_station["station_id"] = station_id  # ground_info에서 사용할 station_id 추가
                
                # 실시간 관측 데이터가 있으면 추가
                if station_id in obs_dict:
                    obs_data = obs_dict[station_id]
                    combined_station.update({
                        "wind_direction": obs_data.get("wind_direction"),
                        "wind_speed": obs_data.get("wind_speed"),
                        "gust_speed": obs_data.get("gust_speed"),
                        "pressure": obs_data.get("pressure"),
                        "temperature": obs_data.get("temperature"),
                        "humidity": obs_data.get("humidity"),
                        "wave_height": obs_data.get("wave_height"),
                        "observed_at": obs_data.get("datetime")
                    })
                
                combined_stations.append(combined_station)
            
            # 4. 관측 데이터 저장
            affected_rows = await self.station_repo.upsert_ground_info(combined_stations)
            
            return {
                "success": True,
                "message": f"Surface data synced successfully",
                "fetched_count": len(combined_stations),
                "affected_rows": affected_rows,
                "station_count": station_rows
            }
            
        except Exception as e:
            print(f"❌ Surface data sync failed: {e}")
            return {"success": False, "message": str(e), "count": 0}