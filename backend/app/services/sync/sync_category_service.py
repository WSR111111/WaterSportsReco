import httpx
from typing import Dict, Any
from ..clients.tourist_client import fetch_category_codes
from ..db.manager import DatabaseManager
from ..db.repositories.sports_repository import SportsRepository


class SyncCategoryService:
    """카테고리 데이터 동기화 서비스"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
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
    
    async def sync_category_data(self, content_type_id: str = "28", 
                               cat1: str = "A03", cat2: str = "A0303") -> Dict[str, Any]:
        """카테고리 코드 데이터 동기화"""
        try:
            print("🏷️ Starting category data sync...")
            
            categories = await fetch_category_codes(
                client=self.http_client,
                content_type_id=content_type_id,
                cat1=cat1,
                cat2=cat2,
                num_of_rows=100
            )
            
            if not categories:
                return {"success": False, "message": "No category data fetched", "count": 0}
            
            affected_rows = await self.sports_repo.upsert_sports_categories(categories)
            
            return {
                "success": True,
                "message": f"Category data synced successfully",
                "fetched_count": len(categories),
                "affected_rows": affected_rows
            }
            
        except Exception as e:
            print(f"❌ Category data sync failed: {e}")
            return {"success": False, "message": str(e), "count": 0}