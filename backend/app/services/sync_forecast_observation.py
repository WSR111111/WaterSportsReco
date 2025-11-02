"""
app/services/sync_forecast_observation.py
────────────────────────────────────────────
- 단기/중기 예보 데이터를 기상청 API로부터 가져와
  CSV 저장 및 observation_data_short / observation_data_medium 테이블에 저장
"""

import re
from datetime import datetime
from app.utils.kma_client import (
    fetch_land_forecast,
    fetch_marine_forecast,
    fetch_medium_land_forecast,
    fetch_medium_marine_forecast,
)
from app.database import DatabaseManager
from app.services.csv_manager import CSVManager


# =========================================================
# 공통 유틸
# =========================================================
def parse_kma_datetime(dt_str: str):
    """YYYYMMDDHH 또는 YYYYMMDDHHMM 문자열 → datetime 변환"""
    if not dt_str or not isinstance(dt_str, str):
        return None
    try:
        cleaned = dt_str.strip().replace("\r", "").replace("\n", "").replace(" ", "")
        if len(cleaned) == 10:
            return datetime.strptime(cleaned, "%Y%m%d%H")
        elif len(cleaned) == 12:
            return datetime.strptime(cleaned, "%Y%m%d%H%M")
        return None
    except Exception as e:
        print(f"⚠️ 날짜 파싱 실패: {dt_str} → {e}")
        return None


# =========================================================
# 단기 예보 (육상)
# =========================================================
def parse_short_term_land(text: str):
    records = []
    for line in text.splitlines():
        if not line or line.startswith("#"):
            continue

        parts = re.split(r"\s+", line.strip())
        if len(parts) < 17:
            continue

        reg_id, tm_fc_str, tm_ef_str = parts[0], parts[1], parts[2]
        tm_fc, tm_ef = parse_kma_datetime(tm_fc_str), parse_kma_datetime(tm_ef_str)

        field_map = {
            "forecast_ground_W1": parts[9],
            "forecast_ground_W2": parts[11],
            "forecast_ground_TA": parts[12],
            "forecast_ground_ST": parts[13],
            "forecast_ground_SKY": parts[14],
            "forecast_ground_PREP": parts[15],
            "forecast_ground_WF": parts[16] if len(parts) > 16 else None,
        }

        for obs_code, obs_value in field_map.items():
            if obs_value:
                records.append({
                    "station_id": reg_id,
                    "obs_code": obs_code,
                    "obs_value": obs_value,
                    "tm_fc": tm_fc,
                    "tm_ef": tm_ef
                })
    return records


# =========================================================
# 단기 예보 (해상)
# =========================================================
def parse_short_term_ocean(text: str):
    records = []
    for line in text.splitlines():
        if not line or line.startswith("#"):
            continue

        parts = re.split(r"\s+", line.strip())
        if len(parts) < 18:
            continue

        reg_id, tm_fc_str, tm_ef_str = parts[0], parts[1], parts[2]
        tm_fc, tm_ef = parse_kma_datetime(tm_fc_str), parse_kma_datetime(tm_ef_str)

        field_map = {
            "forecast_ocean_W1": parts[9],
            "forecast_ocean_W2": parts[11],
            "forecast_ocean_S1": parts[12],
            "forecast_ocean_S2": parts[13],
            "forecast_ocean_WH1": parts[14],
            "forecast_ocean_WH2": parts[15],
            "forecast_ocean_SKY": parts[16],
            "forecast_ocean_PREP": parts[17],
            "forecast_ocean_WF": parts[18] if len(parts) > 18 else None,
        }

        for obs_code, obs_value in field_map.items():
            if obs_value:
                records.append({
                    "station_id": reg_id,
                    "obs_code": obs_code,
                    "obs_value": obs_value,
                    "tm_fc": tm_fc,
                    "tm_ef": tm_ef
                })
    return records


# =========================================================
# 중기 예보 (육상)
# =========================================================
def parse_medium_term_land(text: str):
    records = []
    for line in text.splitlines():
        if not line or line.startswith("#"):
            continue

        parts = re.split(r"\s+", line.strip())
        if len(parts) < 11:
            continue

        reg_id, tm_fc_str, tm_ef_str = parts[0], parts[1], parts[2]
        tm_fc, tm_ef = parse_kma_datetime(tm_fc_str), parse_kma_datetime(tm_ef_str)

        field_map = {
            "forecast_ground_PREP": parts[7],
            "forecast_ground_WF": parts[9],
            "forecast_ground_ST": parts[10] if len(parts) > 10 else None,
            "forecast_ground_SKY": parts[6],
        }

        for obs_code, obs_value in field_map.items():
            if obs_value:
                records.append({
                    "station_id": reg_id,
                    "obs_code": obs_code,
                    "obs_value": obs_value,
                    "tm_fc": tm_fc,
                    "tm_ef": tm_ef
                })
    return records


# =========================================================
# 중기 예보 (해상)
# =========================================================
def parse_medium_term_ocean(text: str):
    records = []
    for line in text.splitlines():
        if not line or line.startswith("#"):
            continue

        parts = re.split(r"\s+", line.strip())
        if len(parts) < 11:
            continue

        reg_id, tm_fc_str, tm_ef_str = parts[0], parts[1], parts[2]
        tm_fc, tm_ef = parse_kma_datetime(tm_fc_str), parse_kma_datetime(tm_ef_str)

        field_map = {
            "forecast_ocean_WH1": parts[6],
            "forecast_ocean_WH2": parts[7],
            "forecast_ocean_SKY": parts[8],
            "forecast_ocean_PREP": parts[9],
            "forecast_ocean_WF": parts[10] if len(parts) > 10 else None,
        }

        for obs_code, obs_value in field_map.items():
            if obs_value:
                records.append({
                    "station_id": reg_id,
                    "obs_code": obs_code,
                    "obs_value": obs_value,
                    "tm_fc": tm_fc,
                    "tm_ef": tm_ef
                })
    return records


# =========================================================
# 데이터 저장 로직
# =========================================================
def save_to_db(records, table_name):
    db = DatabaseManager()
    if not db.connect():
        return {"status": "fail", "message": "DB 연결 실패"}

    try:
        count = 0
        with db.get_connection() as conn:
            with conn.cursor() as cur: 
                for rec in records:
                    cur.execute(
                        f"""
                        INSERT INTO {table_name} (station_id, obs_code, obs_value, tm_fc, tm_ef)
                        VALUES (%s, %s, %s, %s, %s)
                        """,
                        (
                            rec["station_id"],
                            rec["obs_code"],
                            rec["obs_value"],
                            rec["tm_fc"],
                            rec["tm_ef"],
                        ),
                    )
                    count += 1
                conn.commit()

        print(f"💾 {table_name} {count}개 저장 완료")
        return {"status": "success", "count": count}

    except Exception as e:
        print(f"❌ DB 저장 중 오류 발생: {e}")
        return {"status": "fail", "message": str(e)}

    finally:
        db.disconnect()



# =========================================================
# 단기 예보 전체 수집
# =========================================================
def sync_short_term_forecast():
    print("📡 [KMA] 단기 육상 예보 수집 중...")
    land_text = fetch_land_forecast(help=0, disp=0)
    land_records = parse_short_term_land(land_text)

    print("📡 [KMA] 단기 해상 예보 수집 중...")
    ocean_text = fetch_marine_forecast(help=0, disp=0)
    ocean_records = parse_short_term_ocean(ocean_text)

    all_records = land_records + ocean_records
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    csv_manager = CSVManager()
    csv_path = csv_manager.save_to_csv(all_records, "observation_data_short", timestamp)
    print(f"💾 CSV 저장 완료: {csv_path} (총 {len(all_records)}행)")

    return save_to_db(all_records, "observation_data_short")


# =========================================================
# 중기 예보 전체 수집
# =========================================================
def sync_medium_term_forecast():
    print("📡 [KMA] 중기 육상 예보 수집 중...")
    land_text = fetch_medium_land_forecast(help=0, disp=0)
    land_records = parse_medium_term_land(land_text)

    print("📡 [KMA] 중기 해상 예보 수집 중...")
    ocean_text = fetch_medium_marine_forecast(help=0, disp=0)
    ocean_records = parse_medium_term_ocean(ocean_text)

    all_records = land_records + ocean_records
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    csv_manager = CSVManager()
    csv_path = csv_manager.save_to_csv(all_records, "observation_data_medium", timestamp)
    print(f"💾 CSV 저장 완료: {csv_path} (총 {len(all_records)}행)")

    return save_to_db(all_records, "observation_data_medium")


# =========================================================
# 전체 통합 실행
# =========================================================
def sync_all_forecast(debug: bool = False):
    print("🚀 [SYNC] 단기 + 중기 예보 전체 수집 시작")

    result_short = sync_short_term_forecast()
    result_medium = sync_medium_term_forecast()

    print("\n📊 [SYNC 결과 요약]")
    print(f" - 단기 예보 저장: {result_short.get('count', 0)}개")
    print(f" - 중기 예보 저장: {result_medium.get('count', 0)}개")

    return {
        "short_term": result_short,
        "medium_term": result_medium,
        "status": "success"
    }
