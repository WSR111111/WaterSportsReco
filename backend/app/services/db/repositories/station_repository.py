from typing import List, Dict, Any
from ..manager import DatabaseManager


class StationRepository:
    """관측소 관련 데이터베이스 작업"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
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