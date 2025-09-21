import asyncio
import httpx
import mysql.connector
from mysql.connector import Error
from typing import List, Dict, Any, Optional
import os
from ..config import KMA_API_KEY, TOURIST_API_KEY
from .kma.marine_client import fetch_all_marine_stations
from .kma_surface_client import fetch_surface_station_info, fetch_surface_obs
from .tourist_client import fetch_leisure_places_json, fetch_detail_common_json
import json


def _parse_category_data(response_text: str) -> List[Dict[str, Any]]:
    """
    JSON 응답을 파싱하여 카테고리 정보를 반환
    """
    try:
        data = json.loads(response_text)
        
        # API 응답 구조 확인
        response = data.get('response', {})
        header = response.get('header', {})
        
        # 응답 상태 확인
        result_code = header.get('resultCode', '')
        if result_code != '0000':
            result_msg = header.get('resultMsg', 'Unknown error')
            print(f"❌ API Error: {result_code} - {result_msg}")
            return []
        
        # 데이터 추출
        body = response.get('body', {})
        items = body.get('items', {})
        
        # item이 리스트인지 단일 객체인지 확인
        item_data = items.get('item', [])
        if isinstance(item_data, dict):
            item_data = [item_data]
        elif not isinstance(item_data, list):
            item_data = []
        
        categories = []
        for item in item_data:
            try:
                category = {
                    "code": item.get('code', ''),
                    "name": item.get('name', ''),
                    "rnum": item.get('rnum', 0)
                }
                
                # 필수 필드 검증
                if category["code"] and category["name"]:
                    categories.append(category)
                else:
                    print(f"⚠️ Skipping invalid category: {item}")
                    
            except Exception as e:
                print(f"❌ Error parsing category item: {e}")
                continue
        
        print(f"✅ Parsed {len(categories)} categories from API response")
        return categories
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        return []
    except Exception as e:
        print(f"❌ Unexpected error in category data parsing: {e}")
        return []


async def fetch_category_codes(
    client: httpx.AsyncClient,
    content_type_id: str = "28",
    cat1: str = "A03", 
    cat2: str = "A0303",
    num_of_rows: int = 100,
    page_no: int = 1
) -> List[Dict[str, Any]]:
    """
    한국관광공사 카테고리 코드 API를 호출하여 카테고리 정보를 가져옴
    """
    url = "https://apis.data.go.kr/B551011/KorService2/categoryCode2"
    
    params = {
        "serviceKey": TOURIST_API_KEY,
        "numOfRows": num_of_rows,
        "pageNo": page_no,
        "MobileOS": "ETC",
        "MobileApp": "AppTest",
        "contentTypeId": content_type_id,
        "cat1": cat1,
        "cat2": cat2,
        "_type": "json"
    }
    
    try:
        print(f"🔍 Fetching category codes from API...")
        
        response = await client.get(url, params=params, timeout=30.0)
        response.raise_for_status()
        
        print(f"✅ API response received (status: {response.status_code})")
        
        # JSON 응답 파싱
        categories = _parse_category_data(response.text)
        
        if not categories:
            print("⚠️ No categories found in API response")
            return []
        
        print(f"✅ Successfully fetched {len(categories)} categories")
        return categories
        
    except httpx.TimeoutException:
        print("❌ API request timeout (30 seconds)")
        return []
    except httpx.HTTPStatusError as e:
        print(f"❌ HTTP error {e.response.status_code}: {e.response.text}")
        return []
    except httpx.RequestError as e:
        print(f"❌ Network error: {e}")
        return []
    except Exception as e:
        print(f"❌ Unexpected error fetching categories: {e}")
        return []


class DatabaseManager:
    """데이터베이스 연결 및 작업 관리"""
    
    def __init__(self):
        self.connection = None
        # 환경 변수에서 데이터베이스 설정 로드 (보안상 기본값 없음)
        mysql_password = os.getenv('MYSQL_PASSWORD')
        if not mysql_password:
            raise ValueError("MYSQL_PASSWORD environment variable is required for security")
        
        self.db_config = {
            'host': os.getenv('MYSQL_HOST', 'localhost'),
            'database': os.getenv('MYSQL_DATABASE', 'watersportsdb'),
            'user': os.getenv('MYSQL_USER', 'watersports_user'),
            'password': mysql_password,
            'port': int(os.getenv('MYSQL_PORT', 3306)), 
            'charset': 'utf8mb4',
            'autocommit': True
        }
    
    async def connect(self):
        """데이터베이스 연결"""
        try:
            self.connection = mysql.connector.connect(**self.db_config)
            print("✅ Database connected successfully")
            return True
        except Error as e:
            print(f"❌ Database connection failed: {e}")
            return False
    
    async def disconnect(self):
        """데이터베이스 연결 해제"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("✅ Database disconnected")
    
    async def execute_query(self, query: str, params: tuple = None):
        """쿼리 실행"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            result = cursor.fetchall()
            cursor.close()
            return result
        except Error as e:
            print(f"❌ Query execution failed: {e}")
            return None


class SyncService:
    """API 데이터 동기화 서비스"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.http_client = None
    
    async def __aenter__(self):
        """비동기 컨텍스트 매니저 진입"""
        await self.db.connect()
        self.http_client = httpx.AsyncClient(timeout=120.0)  # 타임아웃 2분으로 증가
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """비동기 컨텍스트 매니저 종료"""
        if self.http_client:
            await self.http_client.aclose()
        await self.db.disconnect()
    

    

    
    async def validate_sigungu_code(self, sigungu_code: str) -> bool:
        """시군구 코드가 region 테이블에 존재하는지 검증"""
        try:
            query = "SELECT COUNT(*) FROM region WHERE ldong_sigungu_cd = %s"
            result = await self.db.execute_query(query, (sigungu_code,))
            return result and result[0][0] > 0
        except Exception as e:
            print(f"❌ Failed to validate sigungu_code {sigungu_code}: {e}")
            return False
    
    async def validate_cat3_code(self, cat3: str) -> bool:
        """카테고리 코드가 sports 테이블에 존재하는지 검증"""
        try:
            query = "SELECT COUNT(*) FROM sports WHERE category_code = %s"
            result = await self.db.execute_query(query, (cat3,))
            return result and result[0][0] > 0
        except Exception as e:
            print(f"❌ Failed to validate cat3 {cat3}: {e}")
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
            # ldong_regn_nm: 지역명, ldong_sigungu_nm: 시군구명
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


    async def upsert_ground_stations(self, stations: List[Dict[str, Any]]) -> int:
        """지상 관측소 정보를 ground_stations 테이블에 upsert"""
        if not stations:
            return 0
        
        affected_rows = 0
        for station in stations:
            try:
                station_id = station.get('stnid')
                station_name = station.get('stn_ko')
                lat = station.get('lat')
                lon = station.get('lon')
                fct_id = station.get('fct_id')
                
                if not station_id or not station_name or lat is None or lon is None:
                    continue
                
                upsert_sql = """
                    INSERT INTO ground_stations (station_id, station_name, latitude, longitude, fct_id)
                    VALUES (%s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    station_name = VALUES(station_name),
                    latitude = VALUES(latitude),
                    longitude = VALUES(longitude),
                    fct_id = VALUES(fct_id)
                """
                cursor = self.db.connection.cursor()
                cursor.execute(upsert_sql, (station_id, station_name, lat, lon, fct_id))
                affected_rows += cursor.rowcount
                cursor.close()
                
            except Exception as e:
                print(f"❌ Failed to upsert ground station {station.get('stnid')}: {e}")
                continue
        
        print(f"✅ Upserted {affected_rows} ground station records")
        return affected_rows

    async def upsert_ocean_info(self, stations: List[Dict[str, Any]]) -> int:
        """해양 관측 정보를 ocean_info 테이블에 upsert"""
        if not stations:
            print("⚠️ No ocean data to upsert")
            return 0
        
        print(f"🌊 Upserting {len(stations)} ocean info records...")
        
        affected_rows = 0
        for i, station in enumerate(stations):
            try:
                station_id = station.get('station_id')
                observed_at = station.get('observed_at')
                wave_height = station.get('wave_height')
                water_temp = station.get('sst')
                
                station_name = station.get('station_name')
                lat = station.get('lat')
                lon = station.get('lon')
                
                if not station_id:
                    continue
                
                # 시간 형식 변환
                if observed_at and len(observed_at) >= 12:
                    try:
                        dt_str = f"{observed_at[:4]}-{observed_at[4:6]}-{observed_at[6:8]} {observed_at[8:10]}:{observed_at[10:12]}:00"
                    except Exception as time_err:
                        dt_str = None
                else:
                    dt_str = None
                
                if dt_str is None:
                    continue
                
                # 관측소 정보와 관측 데이터를 함께 저장
                upsert_sql = """
                    INSERT INTO ocean_info (station_id, station_name, latitude, longitude, observation_time, wave_height, water_temp)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    station_name = VALUES(station_name),
                    latitude = VALUES(latitude),
                    longitude = VALUES(longitude),
                    wave_height = VALUES(wave_height),
                    water_temp = VALUES(water_temp)
                """
                cursor = self.db.connection.cursor()
                cursor.execute(upsert_sql, (station_id, station_name, lat, lon, dt_str, wave_height, water_temp))
                affected_rows += cursor.rowcount
                cursor.close()
                
            except Exception as e:
                print(f"❌ Failed to upsert ocean info for station {station.get('station_id')}: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        print(f"✅ Upserted {affected_rows} ocean info records")
        return affected_rows 
    
    async def upsert_ground_info(self, stations: List[Dict[str, Any]]) -> int:
        """지상 관측 정보를 ground_info 테이블에 upsert"""
        if not stations:
            print("⚠️ No ground data to upsert")
            return 0
        
        print(f"🌤️ Upserting {len(stations)} ground info records...")
        
        affected_rows = 0
        for i, station in enumerate(stations):
            try:
                station_id = station.get('station_id')
                observed_at = station.get('observed_at') or station.get('datetime')  # datetime 필드도 확인
                wind_speed = station.get('wind_speed')
                temperature = station.get('temperature')
                humidity = station.get('humidity')
                
                if not station_id:
                    continue
                
                # 시간 형식 변환
                if observed_at and len(observed_at) >= 10:
                    try:
                        if len(observed_at) == 10:  # YYMMDDHHMI 형식
                            # 20을 앞에 붙여서 4자리 연도로 변환
                            dt_str = f"20{observed_at[:2]}-{observed_at[2:4]}-{observed_at[4:6]} {observed_at[6:8]}:{observed_at[8:10]}:00"
                        else:  # 12자리 형식
                            dt_str = f"{observed_at[:4]}-{observed_at[4:6]}-{observed_at[6:8]} {observed_at[8:10]}:{observed_at[10:12]}:00"
                    except Exception as time_err:
                        dt_str = None
                else:
                    dt_str = None
                
                if dt_str is None:
                    continue
                
                upsert_sql = """
                    INSERT INTO ground_info (station_id, observation_time, wind_speed, temp, humidity)
                    VALUES (%s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    wind_speed = VALUES(wind_speed),
                    temp = VALUES(temp),
                    humidity = VALUES(humidity)
                """
                cursor = self.db.connection.cursor()
                cursor.execute(upsert_sql, (station_id, dt_str, wind_speed, temperature, humidity))
                affected_rows += cursor.rowcount
                cursor.close()
                
            except Exception as e:
                print(f"❌ Failed to upsert ground info for station {station.get('station_id')}: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        print(f"✅ Upserted {affected_rows} ground info records")
        return affected_rows
    
    async def upsert_leisure_places(self, spots: List[Dict[str, Any]]) -> int:
        """관광지 데이터를 leisure_place와 place_detail 테이블에 upsert"""
        if not spots:
            return 0
        
        affected_rows = 0
        for spot in spots:
            try:
                lat = spot.get('mapy')
                lon = spot.get('mapx')
                title = spot.get('title', 'Unknown')
                
                if lat is None or lon is None:
                    continue
                
                # sigungu_code 검증 (필수 필드)
                sigungu_code = spot.get('sigungucode', '')
                if not sigungu_code:
                    print(f"⚠️ Skipping leisure place {title}: missing sigungu_code")
                    continue
                
                # cat3 검증 (외래키 제약조건)
                cat3 = spot.get('cat3', '')
                if not cat3:
                    print(f"⚠️ Skipping leisure place {title}: missing cat3")
                    continue
                
                # 외래키 제약조건 검증 및 필요시 생성
                area_code = spot.get('areacode', '')
                if not await self.ensure_region_exists_by_sigungu(sigungu_code, area_code):
                    print(f"⚠️ Skipping leisure place {title}: failed to ensure region exists for sigungu_code {sigungu_code}")
                    continue
                
                if not await self.ensure_sport_exists_by_cat3(cat3):
                    print(f"⚠️ Skipping leisure place {title}: failed to ensure sport exists for cat3 {cat3}")
                    continue
                
                # 새로운 테이블 스키마에 맞춘 INSERT 문
                leisure_upsert_sql = """
                    INSERT INTO leisure_place 
                    (cat3, content_id, place_name, address, address2, 
                     phone_number, latitude, longitude, area_code, sigungu_code,
                     first_image, first_image2)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    cat3 = VALUES(cat3),
                    place_name = VALUES(place_name),
                    address = VALUES(address),
                    address2 = VALUES(address2),
                    phone_number = VALUES(phone_number),
                    latitude = VALUES(latitude),
                    longitude = VALUES(longitude),
                    area_code = VALUES(area_code),
                    sigungu_code = VALUES(sigungu_code),
                    first_image = VALUES(first_image),
                    first_image2 = VALUES(first_image2)
                """
                cursor = self.db.connection.cursor() 
                cursor.execute(leisure_upsert_sql, (
                    cat3,
                    spot.get('content_id', ''),
                    title,
                    spot.get('addr1', ''),
                    spot.get('addr2', ''),
                    spot.get('tel', ''),
                    lat,
                    lon,
                    spot.get('areacode', ''),
                    sigungu_code,
                    spot.get('firstimage', ''),
                    spot.get('firstimage2', '')
                ))
                
                affected_rows += cursor.rowcount
                cursor.close()
                
            except Exception as e:
                print(f"❌ Failed to upsert leisure place for {spot.get('title')}: {e}")
                # 외래키 제약조건 위반 등의 상세 에러 로깅
                if "foreign key constraint" in str(e).lower():
                    print(f"   🔗 Foreign key constraint violation - sigungu_code: {spot.get('sigungucode')}, cat3: {spot.get('cat3')}")
                continue
        
        print(f"✅ Upserted {affected_rows} leisure places")
        return affected_rows
    

    
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
    
    async def upsert_place_details(self, details: List[Dict[str, Any]]) -> int:
        """장소 상세정보를 place_detail 테이블에 upsert"""
        if not details:
            return 0
        
        affected_rows = 0
        for detail in details:
            try:
                content_id = detail.get('contentid', '')
                homepage = detail.get('homepage', '')
                overview = detail.get('overview', '')
                
                if not content_id:
                    print(f"⚠️ Skipping detail with missing content_id: {detail}")
                    continue
                
                upsert_sql = """
                    INSERT INTO place_detail (content_id, homepage, overview)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    homepage = VALUES(homepage),
                    overview = VALUES(overview)
                """
                cursor = self.db.connection.cursor()
                cursor.execute(upsert_sql, (content_id, homepage, overview))
                affected_rows += cursor.rowcount
                cursor.close()
                
            except Exception as e:
                print(f"❌ Failed to upsert detail for content_id {detail.get('contentid', 'Unknown')}: {e}")
                continue
        
        print(f"✅ Upserted {affected_rows} place details")
        return affected_rows
    
    async def sync_marine_data(self, tm: Optional[str] = None) -> Dict[str, Any]:
        """해양 관측소 데이터 동기화"""
        try:
            print("🌊 Starting marine data sync...")
            
            # 해양 관측 데이터 가져오기 (관측소 정보 포함)
            stations = await fetch_all_marine_stations(self.http_client, tm)
            
            if not stations:
                return {"success": False, "message": "No marine data fetched", "count": 0}
            
            affected_rows = await self.upsert_ocean_info(stations)
            
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
            station_rows = await self.upsert_ground_stations(stations_info)
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
            affected_rows = await self.upsert_ground_info(combined_stations)
            
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
            
            affected_rows = await self.upsert_leisure_places(leisure_places)
            
            return {
                "success": True,
                "message": f"Leisure places data synced successfully",
                "fetched_count": len(leisure_places),
                "affected_rows": affected_rows
            }
            
        except Exception as e:
            print(f"❌ Leisure places data sync failed: {e}")
            return {"success": False, "message": str(e), "count": 0}
    
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
            
            affected_rows = await self.upsert_sports_categories(categories)
            
            return {
                "success": True,
                "message": f"Category data synced successfully",
                "fetched_count": len(categories),
                "affected_rows": affected_rows
            }
            
        except Exception as e:
            print(f"❌ Category data sync failed: {e}")
            return {"success": False, "message": str(e), "count": 0}
    
    async def sync_region_data(self) -> Dict[str, Any]:
        """지역 데이터 동기화 (관광공사 API 기반)"""
        try:
            print("🗺️ Starting region data sync...")
            
            # 관광공사 지역 코드 API 호출
            regions = await self._fetch_area_codes()
            
            if not regions:
                return {"success": False, "message": "No region data fetched", "count": 0}
            
            affected_rows = await self.upsert_regions(regions)
            
            return {
                "success": True,
                "message": f"Region data synced successfully",
                "fetched_count": len(regions),
                "affected_rows": affected_rows
            }
            
        except Exception as e:
            print(f"❌ Region data sync failed: {e}")
            return {"success": False, "message": str(e), "count": 0}
    
    async def _fetch_area_codes(self) -> List[Dict[str, Any]]:
        """관광공사 API에서 지역 코드 정보를 가져옴"""
        url = "https://apis.data.go.kr/B551011/KorService2/areaCode2"
        
        params = {
            "serviceKey": TOURIST_API_KEY,
            "numOfRows": 100,
            "pageNo": 1,
            "MobileOS": "ETC",
            "MobileApp": "AppTest",
            "_type": "json"
        }
        
        try:
            print("🔍 Fetching area codes from API...")
            
            response = await self.http_client.get(url, params=params, timeout=30.0)
            response.raise_for_status()
            
            # JSON 응답 파싱
            data = json.loads(response.text)
            response_data = data.get('response', {})
            header = response_data.get('header', {})
            
            # 응답 상태 확인
            result_code = header.get('resultCode', '')
            if result_code != '0000':
                result_msg = header.get('resultMsg', 'Unknown error')
                print(f"❌ API Error: {result_code} - {result_msg}")
                return []
            
            # 데이터 추출
            body = response_data.get('body', {})
            items = body.get('items', {})
            item_data = items.get('item', [])
            
            if isinstance(item_data, dict):
                item_data = [item_data]
            elif not isinstance(item_data, list):
                item_data = []
            
            regions = []
            for item in item_data:
                try:
                    region = {
                        "code": item.get('code', ''),
                        "name": item.get('name', ''),
                        "rnum": item.get('rnum', 0)
                    }
                    
                    if region["code"] and region["name"]:
                        regions.append(region)
                        
                except Exception as e:
                    print(f"❌ Error parsing region item: {e}")
                    continue
            
            print(f"✅ Parsed {len(regions)} regions from API response")
            return regions
            
        except Exception as e:
            print(f"❌ Error fetching area codes: {e}")
            return []
    
    async def upsert_regions(self, regions: List[Dict[str, Any]]) -> int:
        """지역 데이터를 region 테이블에 upsert"""
        if not regions:
            return 0
        
        affected_rows = 0
        for region in regions:
            try:
                code = region.get('code', '')
                name = region.get('name', '')
                
                if not code or not name:
                    print(f"⚠️ Skipping region with missing code or name: {region}")
                    continue
                
                # region 테이블에 기본 정보 저장
                upsert_sql = """
                    INSERT INTO region (ldong_regn_cd, ldong_regn_nm, ldong_sigungu_cd, ldong_sigungu_nm)
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    ldong_regn_nm = VALUES(ldong_regn_nm),
                    ldong_sigungu_nm = VALUES(ldong_sigungu_nm)
                """
                cursor = self.db.connection.cursor()
                cursor.execute(upsert_sql, (code, name, code, name))
                affected_rows += cursor.rowcount
                cursor.close()
                
            except Exception as e:
                print(f"❌ Failed to upsert region {region.get('name', 'Unknown')}: {e}")
                continue
        
        print(f"✅ Upserted {affected_rows} regions")
        return affected_rows
    

    
    async def sync_place_details_data(self, limit: int = 10, delay: int = 3) -> Dict[str, Any]:
        """leisure_place의 모든 content_id에 대한 상세정보 동기화"""
        try:
            print(f"📋 Starting place details data sync (limit: {limit}, delay: {delay}s)...")
            
            # leisure_place에서 아직 place_detail이 없는 content_id 가져오기
            content_ids_query = """
                SELECT DISTINCT lp.content_id 
                FROM leisure_place lp
                LEFT JOIN place_detail pd ON lp.content_id = pd.content_id
                WHERE lp.content_id IS NOT NULL AND lp.content_id != ''
                AND pd.content_id IS NULL
                LIMIT %s
            """
            result = await self.db.execute_query(content_ids_query, (limit,))
            
            if not result:
                return {"success": False, "message": "No content_ids found in leisure_place", "count": 0}
            
            content_ids = [row[0] for row in result]
            print(f"🔍 Found {len(content_ids)} content_ids to process")
            
            # 각 content_id에 대한 상세정보 가져오기
            details = []
            failed_count = 0
            
            for i, content_id in enumerate(content_ids):
                try:
                    print(f"📋 Processing {i+1}/{len(content_ids)}: {content_id}")
                    
                    detail_info = await fetch_detail_common_json(
                        client=self.http_client,
                        content_id=content_id
                    )
                    
                    if detail_info:
                        details.append(detail_info)
                    else:
                        failed_count += 1
                        print(f"⚠️ Failed to get detail for content_id: {content_id}")
                    
                    # API 호출 간격 조절 (API 한도 초과 방지)
                    if i % 3 == 0 and i > 0:
                        print(f"⏸️ Processed {i} items, taking a longer break to avoid API limits...")
                        await asyncio.sleep(delay * 3)  # 파라미터 기반 긴 대기
                    else:
                        # 매 요청마다 파라미터 기반 대기
                        await asyncio.sleep(delay)
                        
                except Exception as e:
                    failed_count += 1
                    print(f"❌ Error processing content_id {content_id}: {e}")
                    continue
            
            if not details:
                return {"success": False, "message": "No detail data fetched", "count": 0}
            
            # 데이터베이스에 저장
            affected_rows = await self.upsert_place_details(details)
            
            return {
                "success": True,
                "message": f"Place details synced successfully",
                "processed_count": len(content_ids),
                "fetched_count": len(details),
                "failed_count": failed_count,
                "affected_rows": affected_rows
            }
            
        except Exception as e:
            print(f"❌ Place details sync failed: {e}")
            return {"success": False, "message": str(e), "count": 0}


# 편의 함수들
async def sync_marine_stations(tm: Optional[str] = None) -> Dict[str, Any]:
    """해양 관측소 데이터만 동기화"""
    async with SyncService() as sync_service:
        return await sync_service.sync_marine_data(tm)


async def sync_surface_stations(tm: Optional[str] = None) -> Dict[str, Any]:
    """지상 관측소 데이터만 동기화"""
    async with SyncService() as sync_service:
        return await sync_service.sync_surface_data(tm)





async def sync_leisure_places(area_code: Optional[str] = None, 
                            sigungu_code: Optional[str] = None) -> Dict[str, Any]:
    """레저 장소 데이터만 동기화 (JSON API)"""
    async with SyncService() as sync_service:
        return await sync_service.sync_leisure_places_data(area_code, sigungu_code)


async def sync_place_details(limit: int = 10, delay: int = 3) -> Dict[str, Any]:
    """장소 상세정보만 동기화"""
    async with SyncService() as sync_service:
        return await sync_service.sync_place_details_data(limit, delay)


async def sync_categories(content_type_id: str = "28", 
                        cat1: str = "A03", cat2: str = "A0303") -> Dict[str, Any]:
    """카테고리 코드 데이터만 동기화"""
    async with SyncService() as sync_service:
        return await sync_service.sync_category_data(content_type_id, cat1, cat2)


async def sync_regions() -> Dict[str, Any]:
    """지역 데이터 동기화"""
    async with SyncService() as sync_service:
        return await sync_service.sync_region_data()


async def sync_ground_stations() -> Dict[str, Any]:
    """지상 관측소 정보만 동기화"""
    from .kma_surface_client import fetch_surface_station_info
    
    async with SyncService() as sync_service:
        try:
            # 기상청 SFC API에서 관측소 정보 가져오기
            station_info = await fetch_surface_station_info(sync_service.http_client)
            
            if not station_info:
                return {"success": False, "message": "No ground station info fetched", "count": 0}
            
            # ground_stations 테이블에 저장
            affected_rows = await sync_service.upsert_ground_stations(station_info)
            
            return {
                "success": True,
                "message": f"Ground stations synced successfully",
                "fetched_count": len(station_info),
                "affected_rows": affected_rows
            }
            
        except Exception as e:
            return {"success": False, "message": str(e), "count": 0}


