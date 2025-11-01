import re
from datetime import datetime
from app.utils.kma_client import fetch_surface_stations, fetch_buoy_stations
from app.database import DatabaseManager
from app.services.csv_manager import CSVManager

def parse_station_response(text: str, category: str):
    """
    기상청 관측소 응답 텍스트를 파싱해서 dict 리스트 반환
    category: 'SURFACE' | 'MARINE'
    
    API 응답 구조:
    - 해양관측소: STN_KO는 인덱스 6
    - 지상관측소: STN_KO는 인덱스 10
    """
    stations = []
    
    for line in text.splitlines():
        line = line.strip()
        # 숫자로 시작하는 라인만 데이터 (관측소 ID)
        if not re.match(r"^\d+", line):
            continue

        parts = re.split(r"\s+", line)
        try:
            station_id = parts[0]
            lon = parts[1]
            lat = parts[2]
            
            # 카테고리별 STN_KO 위치에서 한글명 추출
            station_nm = ""
            
            if category == "MARINE":
                # 해양관측소: STN_KO는 인덱스 6
                if len(parts) > 6:
                    station_nm = parts[6]
                    # "----" 같은 빈 값 처리
                    if station_nm == "----" or not station_nm:
                        station_nm = f"Buoy_{station_id}"
            else:  # SURFACE
                # 지상관측소: STN_KO는 인덱스 10
                if len(parts) > 10:
                    station_nm = parts[10]
                    # "----" 같은 빈 값 처리
                    if station_nm == "----" or not station_nm:
                        station_nm = f"Station_{station_id}"
            
            # 여전히 이름을 못 찾으면 기본값 사용
            if not station_nm:
                prefix = "Buoy" if category == "MARINE" else "Station"
                station_nm = f"{prefix}_{station_id}"
                    
        except Exception as e:
            print(f"파싱 오류 - Line: {line}, Error: {e}")
            continue

        stations.append({
            "station_id": station_id,
            "station_nm": station_nm,
            "lat": lat,
            "lon": lon,
            "category": category
        })
    return stations


def sync_all_stations(tm: str = None, debug: bool = False):
    """지상관측소와 해양관측소 정보를 하나의 observation_station CSV로 저장한 후 DB에 저장"""
    if tm is None:
        tm = datetime.now().strftime("%Y%m%d%H%M")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_manager = CSVManager()
    
    try:
        all_csv_data = []
        
        # 1단계: 지상관측소 API 데이터 수집
        print("=== 1단계: 지상관측소 API 데이터 수집 ===")
        surface_text = fetch_surface_stations(tm)
        
        if debug:
            csv_manager.save_api_response({"raw_text": surface_text, "tm": tm}, "surface_stations", timestamp)
        
        # 2단계: 지상관측소 데이터 파싱
        print("=== 2단계: 지상관측소 데이터 파싱 ===")
        surface_stations = parse_station_response(surface_text, "SURFACE")
        
        # 지상관측소 CSV 데이터 변환
        for st in surface_stations:
            csv_row = {
                "station_id": st["station_id"],
                "station_nm": st["station_nm"],
                "lat": st["lat"],
                "lon": st["lon"],
                "obs_cd": "obs_ground",
                "created_at": timestamp
            }
            all_csv_data.append(csv_row)
        
        print(f"파싱된 지상관측소 수: {len(surface_stations)}")
        
        # 3단계: 해양관측소 API 데이터 수집
        print("=== 3단계: 해양관측소 API 데이터 수집 ===")
        buoy_text = fetch_buoy_stations(tm)
        
        if debug:
            csv_manager.save_api_response({"raw_text": buoy_text, "tm": tm}, "buoy_stations", timestamp)
        
        # 4단계: 해양관측소 데이터 파싱
        print("=== 4단계: 해양관측소 데이터 파싱 ===")
        buoy_stations = parse_station_response(buoy_text, "MARINE")
        
        # 해양관측소 CSV 데이터 변환
        for st in buoy_stations:
            csv_row = {
                "station_id": st["station_id"],
                "station_nm": st["station_nm"],
                "lat": st["lat"],
                "lon": st["lon"],
                "obs_cd": "obs_ocean",
                "created_at": timestamp
            }
            all_csv_data.append(csv_row)
        
        print(f"파싱된 해양관측소 수: {len(buoy_stations)}")
        print(f"총 관측소 수: {len(all_csv_data)}")
        
        # 5단계: 통합 CSV 파일로 저장
        print("=== 5단계: 통합 observation_station CSV 파일 저장 ===")
        if all_csv_data:
            csv_file_path = csv_manager.save_to_csv(all_csv_data, "observation_station", timestamp)
            
            # 6단계: CSV에서 읽어서 DB에 저장
            print("=== 6단계: DB 저장 ===")
            return save_stations_csv_to_db(csv_file_path, debug)
        else:
            return {"status": "success", "count": 0, "message": "저장할 관측소 데이터가 없습니다"}
            
    except Exception as e:
        return {"status": "fail", "message": str(e)}


def sync_surface_stations(tm: str = None, debug: bool = False):
    """지상관측소 정보를 CSV로 저장한 후 DB에 저장"""
    if tm is None:
        tm = datetime.now().strftime("%Y%m%d%H%M")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_manager = CSVManager()
    
    try:
        # 1단계: API에서 데이터 수집
        print("=== 1단계: 지상관측소 API 데이터 수집 ===")
        text = fetch_surface_stations(tm)
        
        # 2단계: API 응답 백업 (선택사항 - 디버그 모드에서만)
        if debug:
            print("=== 2단계: API 응답 백업 ===")
            csv_manager.save_api_response({"raw_text": text, "tm": tm}, "surface_stations", timestamp)
        
        # 디버깅용: 원본 응답 일부 출력
        if debug:
            lines = text.splitlines()[:10]  # 처음 10줄
            print("=== 지상관측소 API 응답 샘플 ===")
            for i, line in enumerate(lines):
                print(f"Line {i}: {line}")
                if "STN_ID" in line or "STN_KO" in line:
                    print(f">>> 헤더 라인 발견: {line}")
                    header_parts = re.split(r"\s+", line.strip())
                    for j, part in enumerate(header_parts):
                        print(f"  Header[{j}]: {part}")
                elif i > 0 and re.match(r"^\d+", line.strip()):  # 첫 번째 데이터 라인
                    parts = re.split(r"\s+", line.strip())
                    print(f">>> 첫 번째 데이터 라인 분석:")
                    print(f"Parts count: {len(parts)}")
                    for j, part in enumerate(parts):
                        print(f"  Data[{j}]: {part}")
                    break
        
        # 2단계: 데이터 파싱
        print("=== 2단계: 데이터 파싱 ===")
        stations = parse_station_response(text, "SURFACE")
        
        # 3단계: CSV 데이터 변환
        print("=== 3단계: CSV 데이터 변환 ===")
        csv_data = []
        for st in stations:
            # category를 obs_cd로 변환 (SURFACE -> obs_ground, MARINE -> obs_ocean)
            obs_cd = "obs_ground" if st["category"] == "SURFACE" else "obs_ocean"
            
            csv_row = {
                "station_id": st["station_id"],
                "station_nm": st["station_nm"],
                "lat": st["lat"],
                "lon": st["lon"],
                "obs_cd": obs_cd,
                "created_at": timestamp
            }
            csv_data.append(csv_row)
        
        print(f"파싱된 지상관측소 수: {len(csv_data)}")
        
        # 4단계: CSV 파일로 저장
        print("=== 4단계: CSV 파일 저장 ===")
        if csv_data:
            csv_file_path = csv_manager.save_to_csv(csv_data, "surface_stations", timestamp)
            
            # 6단계: CSV에서 읽어서 DB에 저장
            print("=== 6단계: DB 저장 ===")
            return save_stations_csv_to_db(csv_file_path, debug)
        else:
            return {"status": "success", "count": 0, "message": "저장할 지상관측소 데이터가 없습니다"}
            
    except Exception as e:
        return {"status": "fail", "message": str(e)}


def sync_buoy_stations(tm: str = None, debug: bool = False):
    """해양관측소 정보를 CSV로 저장한 후 DB에 저장"""
    if tm is None:
        tm = datetime.now().strftime("%Y%m%d%H%M")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_manager = CSVManager()
    
    try:
        # 1단계: API에서 데이터 수집
        print("=== 1단계: 해양관측소 API 데이터 수집 ===")
        text = fetch_buoy_stations(tm)
        
        # 2단계: API 응답 백업 (선택사항 - 디버그 모드에서만)
        if debug:
            print("=== 2단계: API 응답 백업 ===")
            csv_manager.save_api_response({"raw_text": text, "tm": tm}, "buoy_stations", timestamp)
        
        # 디버깅용: 원본 응답 일부 출력
        if debug:
            lines = text.splitlines()[:10]  # 처음 10줄
            print("=== 해양관측소 API 응답 샘플 ===")
            for i, line in enumerate(lines):
                print(f"Line {i}: {line}")
                if "STN_ID" in line or "STN_KO" in line:
                    print(f">>> 헤더 라인 발견: {line}")
                    header_parts = re.split(r"\s+", line.strip())
                    for j, part in enumerate(header_parts):
                        print(f"  Header[{j}]: {part}")
                elif i > 0 and re.match(r"^\d+", line.strip()):  # 첫 번째 데이터 라인
                    parts = re.split(r"\s+", line.strip())
                    print(f">>> 첫 번째 데이터 라인 분석:")
                    print(f"Parts count: {len(parts)}")
                    for j, part in enumerate(parts):
                        print(f"  Data[{j}]: {part}")
                    break
        
        # 2단계: 데이터 파싱
        print("=== 2단계: 데이터 파싱 ===")
        stations = parse_station_response(text, "MARINE")
        
        # 3단계: CSV 데이터 변환
        print("=== 3단계: CSV 데이터 변환 ===")
        csv_data = []
        for st in stations:
            # category를 obs_cd로 변환 (SURFACE -> obs_ground, MARINE -> obs_ocean)
            obs_cd = "obs_ground" if st["category"] == "SURFACE" else "obs_ocean"
            
            csv_row = {
                "station_id": st["station_id"],
                "station_nm": st["station_nm"],
                "lat": st["lat"],
                "lon": st["lon"],
                "obs_cd": obs_cd,
                "created_at": timestamp
            }
            csv_data.append(csv_row)
        
        print(f"파싱된 해양관측소 수: {len(csv_data)}")
        
        # 4단계: CSV 파일로 저장
        print("=== 4단계: CSV 파일 저장 ===")
        if csv_data:
            csv_file_path = csv_manager.save_to_csv(csv_data, "buoy_stations", timestamp)
            
            # 5단계: CSV에서 읽어서 DB에 저장
            print("=== 5단계: DB 저장 ===")
            return save_stations_csv_to_db(csv_file_path, debug)
        else:
            return {"status": "success", "count": 0, "message": "저장할 해양관측소 데이터가 없습니다"}
            
    except Exception as e:
        return {"status": "fail", "message": str(e)}


def save_stations_csv_to_db(csv_file_path: str, debug: bool = False):
    """CSV 파일에서 관측소 데이터를 읽어 DB에 저장"""
    db = DatabaseManager()
    if not db.connect():
        return {"status": "fail", "message": "DB 연결 실패"}

    try:
        csv_manager = CSVManager()
        stations = csv_manager.load_from_csv(csv_file_path)
        
        count = 0
        for st in stations:
            query = """
            INSERT INTO observation_station (station_id, station_nm, lat, lon, obs_cd)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (station_id) DO UPDATE SET
                station_nm = EXCLUDED.station_nm,
                lat = EXCLUDED.lat,
                lon = EXCLUDED.lon,
                obs_cd = EXCLUDED.obs_cd,
                updated_at = NOW()
            """
            db.execute_non_query(query, (
                st["station_id"], st["station_nm"], st["lat"], st["lon"], st["obs_cd"]
            ))
            count += 1
            
        return {"status": "success", "count": count, "csv_file": csv_file_path, "sample_stations": stations[:3] if debug else None}
        
    except Exception as e:
        return {"status": "fail", "message": str(e)}
        
    finally:
        db.disconnect()
