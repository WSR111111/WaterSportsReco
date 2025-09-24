import re
from datetime import datetime
from app.utils.kma_client import fetch_surface_stations, fetch_buoy_stations
from app.db.database import DatabaseManager

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


def sync_surface_stations(tm: str = None, debug: bool = False):
    if tm is None:
        tm = datetime.now().strftime("%Y%m%d%H%M")
    
    db = DatabaseManager()
    if not db.connect():
        return {"status": "fail", "message": "DB 연결 실패"}
    try:
        text = fetch_surface_stations(tm)
        
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
        
        stations = parse_station_response(text, "SURFACE")
        
        for st in stations:
            query = """
            INSERT INTO station (station_id, station_nm, lat, lon, category)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                station_nm = VALUES(station_nm),
                lat = VALUES(lat),
                lon = VALUES(lon),
                category = VALUES(category)
            """
            db.execute_non_query(query, (
                st["station_id"], st["station_nm"], st["lat"], st["lon"], st["category"]
            ))
            
        return {"status": "success", "count": len(stations), "sample_stations": stations[:3] if debug else None}
    finally:
        db.disconnect()


def sync_buoy_stations(tm: str = None, debug: bool = False):
    if tm is None:
        tm = datetime.now().strftime("%Y%m%d%H%M")
    
    db = DatabaseManager()
    if not db.connect():
        return {"status": "fail", "message": "DB 연결 실패"}
    try:
        text = fetch_buoy_stations(tm)
        
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
        
        stations = parse_station_response(text, "MARINE")
        
        for st in stations:
            query = """
            INSERT INTO station (station_id, station_nm, lat, lon, category)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                station_nm = VALUES(station_nm),
                lat = VALUES(lat),
                lon = VALUES(lon),
                category = VALUES(category)
            """
            db.execute_non_query(query, (
                st["station_id"], st["station_nm"], st["lat"], st["lon"], st["category"]
            ))
            
        return {"status": "success", "count": len(stations), "sample_stations": stations[:3] if debug else None}
    finally:
        db.disconnect()
