import re
from datetime import datetime
from app.utils.kma_client import fetch_surface_data, fetch_buoy_data
from app.db.database import DatabaseManager

# 지상관측 지표 매핑 (응답 필드 인덱스 → observation_cd)
# 실제 데이터 구조: YYMMDDHHMI STN WD WS GST GST GST PA PS PT PR TA TD HM PV RN ...
#                    0          1   2  3  4   5   6   7  8  9  10 11 12 13 14 15
SURFACE_INDICATORS = {
    2: "WD",   # 풍향 (Wind Direction)
    3: "WS",   # 풍속 (Wind Speed)
    11: "TA",  # 기온 (Temperature Air)
    15: "RN",  # 강수량 (Rain)
}

# 해양관측 지표 매핑 (응답 필드 인덱스 → observation_cd)
BUOY_INDICATORS = {
    2: "WD",       # 풍향
    3: "WS",       # 풍속
    11: "TA",      # 기온
    12: "TW",      # 수온
    14: "WH_SIG",  # 유의파고
    16: "WP",      # 파주기
}

def clean_value(val: str):
    """결측값(-9, -99.0, 9999.9 등)을 None 처리"""
    if val in ["-9", "-9.0", "-99.0", "9999.9", "999.9", "-99", "999"]:
        return None
    try:
        return float(val)
    except ValueError:
        return None

def parse_surface_response(text: str, debug: bool = False):
    """지상관측 응답 텍스트 파싱"""
    data = []
    lines = text.splitlines()
    
    if debug:
        print("=== 지상관측 API 응답 샘플 ===")
        for i, line in enumerate(lines[:5]):
            print(f"Line {i}: {line}")
            if re.match(r"^\d{12}", line.strip()):
                parts = re.split(r"\s+", line.strip())
                print(f">>> 첫 번째 데이터 라인 분석:")
                print(f"Parts count: {len(parts)}")
                for j, part in enumerate(parts):
                    print(f"  [{j}]: {part}")
                break
    
    for line in lines:
        if not re.match(r"^\d{12}", line.strip()):  # 관측시각으로 시작하는 줄만
            continue
        parts = re.split(r"\s+", line.strip())
        
        if len(parts) < 16:  # 최소 필드 수 체크
            if debug:
                print(f"필드 수 부족: {len(parts)} < 16, Line: {line}")
            continue
            
        tm = datetime.strptime(parts[0], "%Y%m%d%H%M")
        station_id = parts[1]
        
        for idx, cd in SURFACE_INDICATORS.items():
            if idx >= len(parts):
                continue
            value = clean_value(parts[idx])
            if value is not None:
                data.append({
                    "station_id": station_id,
                    "observation_cd": cd,
                    "observation_value": value,
                    "observed_at": tm
                })
                if debug:
                    print(f"데이터 추가: {station_id}, {cd}, {value}")
    
    if debug:
        print(f"총 파싱된 레코드 수: {len(data)}")
    
    return data

def parse_buoy_response(text: str):
    """해양관측 응답 텍스트 파싱"""
    data = []
    for line in text.splitlines():
        if not re.match(r"^\d{12}", line.strip()):
            continue
        parts = re.split(r"\s+", line.strip())
        tm = datetime.strptime(parts[0], "%Y%m%d%H%M")
        station_id = parts[1]
        for idx, cd in BUOY_INDICATORS.items():
            if idx >= len(parts):
                continue
            value = clean_value(parts[idx])
            if value is not None:
                data.append({
                    "station_id": station_id,
                    "observation_cd": cd,
                    "observation_value": value,
                    "observed_at": tm
                })
    return data

def sync_surface_observations(tm: str = None, stn: str = "0", debug: bool = False):
    """지상관측 데이터 저장"""
    # tm이 None이면 API가 자동으로 최신 데이터를 반환
    
    db = DatabaseManager()
    if not db.connect():
        return {"status": "fail", "message": "DB 연결 실패"}

    try:
        if debug:
            print(f"요청 시간: {tm if tm else '최신 데이터'}")
        
        text = fetch_surface_data(tm, stn)
        
        if debug:
            print(f"API 응답 길이: {len(text)} 문자")
            print("=== 전체 응답 내용 ===")
            print(text[:1000])  # 처음 1000자만 출력
        
        records = parse_surface_response(text, debug)

        query = """
        INSERT INTO observation_data (station_id, observation_cd, observation_value, observed_at)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            observation_value = VALUES(observation_value),
            observed_at = VALUES(observed_at)
        """

        inserted_count = 0
        for rec in records:
            try:
                db.execute_non_query(query, (
                    rec["station_id"],
                    rec["observation_cd"],
                    rec["observation_value"],
                    rec["observed_at"]
                ))
                inserted_count += 1
                if debug:
                    print(f"DB 저장 성공: {rec['station_id']}, {rec['observation_cd']}, {rec['observation_value']}")
            except Exception as e:
                if debug:
                    print(f"DB 저장 실패: {rec}, Error: {e}")

        return {"status": "success", "count": len(records), "inserted": inserted_count, "sample_records": records[:3] if debug else None}

    except Exception as e:
        return {"status": "fail", "message": str(e)}

    finally:
        db.disconnect()

def sync_buoy_observations(tm: str = None, stn: str = "0", debug: bool = False):
    """해양관측 데이터 저장"""
    # tm이 None이면 API가 자동으로 최신 데이터를 반환
    
    db = DatabaseManager()
    if not db.connect():
        return {"status": "fail", "message": "DB 연결 실패"}

    try:
        if debug:
            print(f"해양관측 요청 시간: {tm if tm else '최신 데이터'}")
        
        text = fetch_buoy_data(tm, stn)
        records = parse_buoy_response(text)

        query = """
        INSERT INTO observation_data (station_id, observation_cd, observation_value, observed_at)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            observation_value = VALUES(observation_value),
            observed_at = VALUES(observed_at)
        """

        for rec in records:
            db.execute_non_query(query, (
                rec["station_id"],
                rec["observation_cd"],
                rec["observation_value"],
                rec["observed_at"]
            ))

        return {"status": "success", "count": len(records)}

    except Exception as e:
        return {"status": "fail", "message": str(e)}

    finally:
        db.disconnect()
