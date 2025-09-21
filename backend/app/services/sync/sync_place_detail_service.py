import asyncio
import httpx
from typing import Dict, Any, List
from ..clients.tourist_client import fetch_detail_common_json
from ..db.manager import DatabaseManager
from ..db.repositories.place_repository import PlaceRepository


class SyncPlaceDetailService:
    """장소 상세정보 동기화 서비스"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.place_repo = PlaceRepository(db_manager)
        self.http_client = None
    
    async def __aenter__(self):
        """비동기 컨텍스트 매니저 진입"""
        self.http_client = httpx.AsyncClient(timeout=120.0)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """비동기 컨텍스트 매니저 종료"""
        if self.http_client:
            await self.http_client.aclose()
    
    async def get_content_ids_without_details(self, limit: int = 10) -> List[str]:
        """상세정보가 없는 content_id 목록을 가져옴"""
        try:
            query = """
                SELECT DISTINCT lp.content_id 
                FROM leisure_place lp 
                LEFT JOIN place_detail pd ON lp.content_id = pd.content_id 
                WHERE pd.content_id IS NULL 
                AND lp.content_id IS NOT NULL 
                AND lp.content_id != ''
                LIMIT %s
            """
            result = await self.db.execute_query(query, (limit,))
            return [row[0] for row in result] if result else []
        except Exception as e:
            print(f"❌ Failed to get content_ids without details: {e}")
            return []
    
    async def sync_place_details_data(self, limit: int = 10, delay: int = 3) -> Dict[str, Any]:
        """장소 상세정보 동기화 (API 제한 고려하여 소량씩 처리)"""
        try:
            print("📋 Starting place details data sync...")
            
            # 상세정보가 없는 content_id 목록 가져오기
            content_ids = await self.get_content_ids_without_details(limit)
            
            if not content_ids:
                return {
                    "success": True,
                    "message": "No content_ids found without details",
                    "processed_count": 0,
                    "success_count": 0,
                    "failed_count": 0
                }
            
            print(f"🔍 Found {len(content_ids)} content_ids without details")
            
            details = []
            success_count = 0
            failed_count = 0
            
            for i, content_id in enumerate(content_ids):
                try:
                    print(f"📋 Fetching detail for content_id: {content_id} ({i+1}/{len(content_ids)})")
                    
                    detail = await fetch_detail_common_json(self.http_client, content_id)
                    
                    if detail:
                        details.append(detail)
                        success_count += 1
                        print(f"✅ Successfully fetched detail for content_id: {content_id}")
                    else:
                        failed_count += 1
                        print(f"⚠️ No detail found for content_id: {content_id}")
                    
                    # API 제한을 고려하여 대기
                    if i < len(content_ids) - 1:  # 마지막이 아닌 경우만 대기
                        print(f"⏳ Waiting {delay} seconds before next API call...")
                        await asyncio.sleep(delay)
                        
                except Exception as e:
                    failed_count += 1
                    print(f"❌ Failed to fetch detail for content_id {content_id}: {e}")
                    continue
            
            # 가져온 상세정보들을 DB에 저장
            affected_rows = 0
            if details:
                affected_rows = await self.place_repo.upsert_place_details(details)
            
            return {
                "success": True,
                "message": f"Place details sync completed",
                "processed_count": len(content_ids),
                "success_count": success_count,
                "failed_count": failed_count,
                "affected_rows": affected_rows
            }
            
        except Exception as e:
            print(f"❌ Place details sync failed: {e}")
            return {"success": False, "message": str(e), "count": 0}