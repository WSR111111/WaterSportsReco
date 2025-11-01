import re
from datetime import datetime
from app.utils.kma_client import fetch_surface_data, fetch_buoy_data
from app.database import DatabaseManager
from app.services.csv_manager import CSVManager

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
    14: "WH",      # 유의파고
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

def sync_all_observations(tm: str = None, stn: str = "0", debug: bool = False):
    """지상관측과 해양관측 데이터를 하나의 observation_data CSV로 저장한 후 DB에 저장"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_manager = CSVManager()
    
    try:
        all_csv_data = []
        
        # 1단계: 지상관측 API 데이터 수집
        print("=== 1단계: 지상관측 API 데이터 수집 ===")
        if debug:
            print(f"지상관측 요청 시간: {tm if tm else '최신 데이터'}")
        
        surface_text = fetch_surface_data(tm, stn)
        
        if debug:
            csv_manager.save_api_response({"raw_text": surface_text, "tm": tm, "stn": stn}, "surface_observations", timestamp)
        
        # 2단계: 지상관측 데이터 파싱
        print("=== 2단계: 지상관측 데이터 파싱 ===")
        surface_records = parse_surface_response(surface_text, debug)
        
        # 지상관측 CSV 데이터 변환
        for rec in surface_records:
            csv_row = {
                "station_id": rec["station_id"],
                "obs_cd": f"obs_ground_{rec['observation_cd']}",  # obs_ground_TA, obs_ground_WS 등
                "observation_value": rec["observation_value"],
                "observed_at": rec["observed_at"].strftime("%Y-%m-%d %H:%M:%S"),
                "created_at": timestamp
            }
            all_csv_data.append(csv_row)
        
        print(f"파싱된 지상관측 데이터 수: {len(surface_records)}")
        
        # 3단계: 해양관측 API 데이터 수집
        print("=== 3단계: 해양관측 API 데이터 수집 ===")
        if debug:
            print(f"해양관측 요청 시간: {tm if tm else '최신 데이터'}")
        
        buoy_text = fetch_buoy_data(tm, stn)
        
        if debug:
            csv_manager.save_api_response({"raw_text": buoy_text, "tm": tm, "stn": stn}, "buoy_observations", timestamp)
        
        # 4단계: 해양관측 데이터 파싱
        print("=== 4단계: 해양관측 데이터 파싱 ===")
        buoy_records = parse_buoy_response(buoy_text)
        
        # 해양관측 CSV 데이터 변환
        for rec in buoy_records:
            csv_row = {
                "station_id": rec["station_id"],
                "obs_cd": f"obs_ocean_{rec['observation_cd']}",  # obs_ocean_TW, obs_ocean_WH 등
                "observation_value": rec["observation_value"],
                "observed_at": rec["observed_at"].strftime("%Y-%m-%d %H:%M:%S"),
                "created_at": timestamp
            }
            all_csv_data.append(csv_row)
        
        print(f"파싱된 해양관측 데이터 수: {len(buoy_records)}")
        print(f"총 관측 데이터 수: {len(all_csv_data)}")
        
        # 5단계: 통합 CSV 파일로 저장
        print("=== 5단계: 통합 observation_data CSV 파일 저장 ===")
        if all_csv_data:
            csv_file_path = csv_manager.save_to_csv(all_csv_data, "observation_data", timestamp)
            
            # 6단계: CSV에서 읽어서 DB에 저장
            print("=== 6단계: DB 저장 ===")
            return save_observations_csv_to_db(csv_file_path, debug)
        else:
            return {"status": "success", "count": 0, "message": "저장할 관측 데이터가 없습니다"}

    except Exception as e:
        return {"status": "fail", "message": str(e)}


def save_observations_csv_to_db(csv_file_path: str, debug: bool = False):
    """CSV 파일에서 관측 데이터를 읽어 DB에 저장"""
    db = DatabaseManager()
    if not db.connect():
        return {"status": "fail", "message": "DB 연결 실패"}

    try:
        csv_manager = CSVManager()
        items = csv_manager.load_from_csv(csv_file_path)
        
        query = """
        INSERT INTO observation_data (station_id, obs_cd, observation_value, observed_at)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (station_id, obs_cd, observed_at) DO UPDATE SET
            observation_value = EXCLUDED.observation_value
        """

        inserted_count = 0
        for item in items:
            try:
                observed_at = datetime.strptime(item["observed_at"], "%Y-%m-%d %H:%M:%S")
                
                db.execute_non_query(query, (
                    item["station_id"],
                    item["obs_cd"],
                    float(item["observation_value"]),
                    observed_at
                ))
                inserted_count += 1
                if debug:
                    print(f"DB 저장 성공: {item['station_id']}, {item['obs_cd']}, {item['observation_value']}")
            except Exception as e:
                if debug:
                    print(f"DB 저장 실패: {item}, Error: {e}")

        return {"status": "success", "count": len(items), "inserted": inserted_count, "csv_file": csv_file_path}

    except Exception as e:
        return {"status": "fail", "message": str(e)}

    finally:
        db.disconnect()


def sync_surface_observations(tm: str = None, stn: str = "0", debug: bool = False):
    """지상관측 데이터를 CSV로 저장한 후 DB에 저장"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_manager = CSVManager()
    
    try:
        # 1단계: API에서 데이터 수집
        print("=== 1단계: 지상관측 API 데이터 수집 ===")
        if debug:
            print(f"요청 시간: {tm if tm else '최신 데이터'}")
        
        text = fetch_surface_data(tm, stn)
        
        if debug:
            print(f"API 응답 길이: {len(text)} 문자")
            print("=== 전체 응답 내용 ===")
            print(text[:1000])  # 처음 1000자만 출력
        
        # 2단계: API 응답 원본을 텍스트로 백업
        print("=== 2단계: API 응답 백업 ===")
        csv_manager.save_api_response({"raw_text": text, "tm": tm, "stn": stn}, "surface_observations", timestamp)
        
        # 3단계: 데이터 파싱
        print("=== 3단계: 데이터 파싱 ===")
        records = parse_surface_response(text, debug)
        
        # 4단계: CSV 형태로 변환
        print("=== 4단계: CSV 데이터 변환 ===")
        csv_data = []
        for rec in records:
            csv_row = {
                "station_id": rec["station_id"],
                "observation_cd": rec["observation_cd"],
                "observation_value": rec["observation_value"],
                "observed_at": rec["observed_at"].strftime("%Y-%m-%d %H:%M:%S"),
                "created_at": timestamp
            }
            csv_data.append(csv_row)
        
        print(f"파싱된 관측 데이터 수: {len(csv_data)}")
        
        # 5단계: CSV 파일로 저장
        print("=== 5단계: CSV 파일 저장 ===")
        if csv_data:
            csv_file_path = csv_manager.save_to_csv(csv_data, "surface_observations", timestamp)
            
            # 6단계: CSV에서 읽어서 DB에 저장
            print("=== 6단계: DB 저장 ===")
            return _save_surface_observations_csv_to_db(csv_file_path, debug)
        else:
            return {"status": "success", "count": 0, "message": "저장할 관측 데이터가 없습니다"}

    except Exception as e:
        return {"status": "fail", "message": str(e)}


def _save_surface_observations_csv_to_db(csv_file_path: str, debug: bool = False):
    """CSV 파일에서 지상관측 데이터를 읽어 DB에 저장"""
    db = DatabaseManager()
    if not db.connect():
        return {"status": "fail", "message": "DB 연결 실패"}

    try:
        csv_manager = CSVManager()
        items = csv_manager.load_from_csv(csv_file_path)
        
        query = """
        INSERT INTO observation_data (station_id, observation_cd, observation_value, observed_at)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            observation_value = VALUES(observation_value),
            observed_at = VALUES(observed_at)
        """

        inserted_count = 0
        for item in items:
            try:
                observed_at = datetime.strptime(item["observed_at"], "%Y-%m-%d %H:%M:%S")
                
                db.execute_non_query(query, (
                    item["station_id"],
                    item["observation_cd"],
                    float(item["observation_value"]),
                    observed_at
                ))
                inserted_count += 1
                if debug:
                    print(f"DB 저장 성공: {item['station_id']}, {item['observation_cd']}, {item['observation_value']}")
            except Exception as e:
                if debug:
                    print(f"DB 저장 실패: {item}, Error: {e}")

        return {"status": "success", "count": len(items), "inserted": inserted_count, "csv_file": csv_file_path}

    except Exception as e:
        return {"status": "fail", "message": str(e)}

    finally:
        db.disconnect()

def sync_buoy_observations(tm: str = None, stn: str = "0", debug: bool = False):
    """해양관측 데이터를 CSV로 저장한 후 DB에 저장"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_manager = CSVManager()
    
    try:
        # 1단계: API에서 데이터 수집
        print("=== 1단계: 해양관측 API 데이터 수집 ===")
        if debug:
            print(f"해양관측 요청 시간: {tm if tm else '최신 데이터'}")
        
        text = fetch_buoy_data(tm, stn)
        
        # 2단계: API 응답 원본을 텍스트로 백업
        print("=== 2단계: API 응답 백업 ===")
        csv_manager.save_api_response({"raw_text": text, "tm": tm, "stn": stn}, "buoy_observations", timestamp)
        
        # 3단계: 데이터 파싱
        print("=== 3단계: 데이터 파싱 ===")
        records = parse_buoy_response(text)
        
        # 4단계: CSV 형태로 변환
        print("=== 4단계: CSV 데이터 변환 ===")
        csv_data = []
        for rec in records:
            csv_row = {
                "station_id": rec["station_id"],
                "observation_cd": rec["observation_cd"],
                "observation_value": rec["observation_value"],
                "observed_at": rec["observed_at"].strftime("%Y-%m-%d %H:%M:%S"),
                "created_at": timestamp
            }
            csv_data.append(csv_row)
        
        print(f"파싱된 해양관측 데이터 수: {len(csv_data)}")
        
        # 5단계: CSV 파일로 저장
        print("=== 5단계: CSV 파일 저장 ===")
        if csv_data:
            csv_file_path = csv_manager.save_to_csv(csv_data, "buoy_observations", timestamp)
            
            # 6단계: CSV에서 읽어서 DB에 저장
            print("=== 6단계: DB 저장 ===")
            return _save_buoy_observations_csv_to_db(csv_file_path, debug)
        else:
            return {"status": "success", "count": 0, "message": "저장할 해양관측 데이터가 없습니다"}

    except Exception as e:
        return {"status": "fail", "message": str(e)}


def _save_buoy_observations_csv_to_db(csv_file_path: str, debug: bool = False):
    """CSV 파일에서 해양관측 데이터를 읽어 DB에 저장"""
    db = DatabaseManager()
    if not db.connect():
        return {"status": "fail", "message": "DB 연결 실패"}

    try:
        csv_manager = CSVManager()
        items = csv_manager.load_from_csv(csv_file_path)
        
        query = """
        INSERT INTO observation_data (station_id, observation_cd, observation_value, observed_at)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            observation_value = VALUES(observation_value),
            observed_at = VALUES(observed_at)
        """

        inserted_count = 0
        for item in items:
            try:
                observed_at = datetime.strptime(item["observed_at"], "%Y-%m-%d %H:%M:%S")
                
                db.execute_non_query(query, (
                    item["station_id"],
                    item["observation_cd"],
                    float(item["observation_value"]),
                    observed_at
                ))
                inserted_count += 1
                if debug:
                    print(f"DB 저장 성공: {item['station_id']}, {item['observation_cd']}, {item['observation_value']}")
            except Exception as e:
                if debug:
                    print(f"DB 저장 실패: {item}, Error: {e}")

        return {"status": "success", "count": len(items), "inserted": inserted_count, "csv_file": csv_file_path}

    except Exception as e:
        return {"status": "fail", "message": str(e)}

    finally:
        db.disconnect()
