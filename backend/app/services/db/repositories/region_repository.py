from typing import List, Dict, Any, Optional
from ..manager import DatabaseManager


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
    
    async def ensure_region_exists_by_sigungu(self, sigungu_code: str, area_code: str = None) -> bool:
        """시군구 코드에 해당하는 region이 없으면 생성"""
        try:
            # 이미 존재하는지 확인
            if await self.validate_sigungu_code(sigungu_code):
                return True
            
            # 기존 region 테이블 구조 확인
            try:
                desc_query = "DESCRIBE region"
                columns_result = await self.db.execute_query(desc_query)
                available_columns = [col[0] for col in columns_result] if columns_result else []
                print(f"🔍 Available region table columns: {available_columns}")
            except Exception as desc_e:
                print(f"⚠️ Could not describe region table: {desc_e}")
                available_columns = []
            
            # 실제 테이블 구조에 맞춘 컬럼명 사용
            region_name = f"지역_{sigungu_code}"
            sigungu_name = f"시군구_{sigungu_code}"
            
            # 동적으로 INSERT 쿼리 생성
            columns = ['ldong_regn_nm', 'ldong_sigungu_cd', 'ldong_sigungu_nm']
            values = [region_name, sigungu_code, sigungu_name]
            
            # ldong_regn_cd가 있다면 추가 (지역코드)
            if 'ldong_regn_cd' in available_columns:
                columns.append('ldong_regn_cd')
                values.append(area_code or sigungu_code[:2])  # 앞 2자리를 지역코드로 사용
            
            columns_str = ', '.join(columns)
            placeholders = ', '.join(['%s'] * len(values))
            
            insert_query = f"""
                INSERT INTO region ({columns_str}) 
                VALUES ({placeholders})
            """
            cursor = self.db.connection.cursor()
            cursor.execute(insert_query, tuple(values))
            cursor.close()
            
            print(f"✅ Created new region for sigungu_code: {sigungu_code}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to ensure region exists for sigungu_code {sigungu_code}: {e}")
            return False