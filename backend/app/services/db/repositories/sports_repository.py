from typing import List, Dict, Any
from ..manager import DatabaseManager


class SportsRepository:
    """스포츠 관련 데이터베이스 작업"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    async def validate_cat3_code(self, cat3: str) -> bool:
        """카테고리 코드가 sports 테이블에 존재하는지 검증"""
        try:
            query = "SELECT COUNT(*) FROM sports WHERE category_code = %s"
            result = await self.db.execute_query(query, (cat3,))
            return result and result[0][0] > 0
        except Exception as e:
            print(f"❌ Failed to validate cat3 {cat3}: {e}")
            return False
    
    async def ensure_sport_exists_by_cat3(self, cat3: str, sport_name: str = None) -> bool:
        """카테고리 코드에 해당하는 sport이 없으면 생성"""
        try:
            # 이미 존재하는지 확인
            if await self.validate_cat3_code(cat3):
                return True
            
            # 새로운 sport 생성
            if not sport_name:
                sport_name = f"스포츠_{cat3}"
            
            insert_query = """
                INSERT INTO sports (sport_name, category_code) 
                VALUES (%s, %s)
            """
            cursor = self.db.connection.cursor()
            cursor.execute(insert_query, (sport_name, cat3))
            cursor.close()
            
            print(f"✅ Created new sport for cat3: {cat3}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to ensure sport exists for cat3 {cat3}: {e}")
            return False
    
    async def upsert_sports_categories(self, categories: List[Dict[str, Any]]) -> int:
        """카테고리 데이터를 sports 테이블에 upsert"""
        if not categories:
            return 0
        
        affected_rows = 0
        for category in categories:
            try:
                code = category.get('code', '')
                name = category.get('name', '')
                
                if not code or not name:
                    print(f"⚠️ Skipping category with missing code or name: {category}")
                    continue
                
                # category_code 컬럼이 있다고 가정하고 UPSERT
                upsert_sql = """
                    INSERT INTO sports (sport_name, category_code)
                    VALUES (%s, %s)
                    ON DUPLICATE KEY UPDATE
                    sport_name = VALUES(sport_name),
                    category_code = VALUES(category_code)
                """
                cursor = self.db.connection.cursor()
                cursor.execute(upsert_sql, (name, code))
                affected_rows += cursor.rowcount
                cursor.close()
                
            except Exception as e:
                print(f"❌ Failed to upsert category {category.get('name', 'Unknown')}: {e}")
                continue
        
        print(f"✅ Upserted {affected_rows} sports categories")
        return affected_rows