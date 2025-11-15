"""
app/services/sync_forecast_station.py
────────────────────────────────────────────
- 기상청 단기/중기 예보 구역정보를 CSV로 저장 후 DB에 저장
(시간대 컬럼 제거 버전)
"""
import re
from datetime import datetime
from app.utils.kma_client import fetch_short_term_station, fetch_medium_term_station
from app.database import DatabaseManager
from app.services.csv_manager import CSVManager


def parse_forecast_station_response(text: str):
    """
    fct_shrt_reg.php, fct_medm_reg.php 응답 파싱
    구조 예시:
        11B00000 199001010000 210012310000 A 서울.인천.경기
    """
    stations = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        # 단기/중기 예보 구역정보는 공백 구분
        parts = re.split(r"\s+", line)
        if len(parts) < 5:
            continue

        reg_id = parts[0].strip()
        reg_sp = parts[3].strip()
        reg_name = parts[4].strip()

        stations.append({
            "reg_id": reg_id,
            "reg_sp": reg_sp,
            "reg_name": reg_name
        })
    return stations


# =========================================================
# 단기 예보 구역 동기화
# =========================================================
def sync_short_term_stations(debug: bool = False):
    """단기예보 구역정보를 CSV로 저장 후 DB 반영"""
    print("📡 [KMA] 단기예보 구역정보 수집 중...")
    text = fetch_short_term_station(help=0, disp=0)
    stations = parse_forecast_station_response(text)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if not stations:
        print("⚠️ 단기예보 구역 데이터가 없습니다.")
        return {"status": "empty"}

    csv_manager = CSVManager()
    csv_rows = []
    for st in stations:
        csv_rows.append({
            "station_id": st["reg_id"],
            "reg_sp": st["reg_sp"],
            "reg_name": st["reg_name"],
            "created_at": timestamp
        })

    print(f"✅ 파싱된 단기예보 구역 수: {len(csv_rows)}")

    csv_path = csv_manager.save_to_csv(csv_rows, "short_term_stations", timestamp)
    print(f"📁 CSV 저장 완료: {csv_path}")

    return save_short_term_stations_to_db(csv_path, debug)


def save_short_term_stations_to_db(csv_path: str, debug: bool = False):
    """CSV → short_term_station 테이블에 저장"""
    db = DatabaseManager()

    try:
        csv_manager = CSVManager()
        stations = csv_manager.load_from_csv(csv_path)
        count = 0

        with db.get_connection() as conn:
            cur = conn.cursor()
            for st in stations:
                cur.execute("""
                    INSERT INTO short_term_station (station_id, reg_sp, reg_name)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (station_id)
                    DO UPDATE SET
                        reg_sp = EXCLUDED.reg_sp,
                        reg_name = EXCLUDED.reg_name;
                """, (st["station_id"], st["reg_sp"], st["reg_name"]))
                count += 1
            conn.commit()

        print(f"💾 단기예보 구역 {count}개 저장 완료")
        return {"status": "success", "count": count, "file": csv_path}

    except Exception as e:
        print(f"❌ 단기예보 저장 중 오류: {e}")
        return {"status": "fail", "message": str(e)}



# =========================================================
# 중기 예보 구역 동기화
# =========================================================
def sync_medium_term_stations(debug: bool = False):
    """중기예보 구역정보를 CSV로 저장 후 DB 반영"""
    print("📡 [KMA] 중기예보 구역정보 수집 중...")
    text = fetch_medium_term_station(help=0, disp=0)
    stations = parse_forecast_station_response(text)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if not stations:
        print("⚠️ 중기예보 구역 데이터가 없습니다.")
        return {"status": "empty"}

    csv_manager = CSVManager()
    csv_rows = []
    for st in stations:
        csv_rows.append({
            "reg_id": st["reg_id"],
            "reg_sp": st["reg_sp"],
            "reg_name": st["reg_name"],
            "created_at": timestamp
        })

    print(f"✅ 파싱된 중기예보 구역 수: {len(csv_rows)}")

    csv_path = csv_manager.save_to_csv(csv_rows, "medium_term_stations", timestamp)
    print(f"📁 CSV 저장 완료: {csv_path}")

    return save_medium_term_stations_to_db(csv_path, debug)


def save_medium_term_stations_to_db(csv_path: str, debug: bool = False):
    """CSV → medium_term_station 테이블에 저장"""
    db = DatabaseManager()

    try:
        csv_manager = CSVManager()
        stations = csv_manager.load_from_csv(csv_path)
        count = 0

        with db.get_connection() as conn:
            cur = conn.cursor()
            for st in stations:
                cur.execute("""
                    INSERT INTO medium_term_station (reg_id, reg_sp, reg_name)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (reg_id)
                    DO UPDATE SET
                        reg_sp = EXCLUDED.reg_sp,
                        reg_name = EXCLUDED.reg_name;
                """, (st["reg_id"], st["reg_sp"], st["reg_name"]))
                count += 1
            conn.commit()

        print(f"💾 중기예보 구역 {count}개 저장 완료")
        return {"status": "success", "count": count, "file": csv_path}

    except Exception as e:
        print(f"❌ 중기예보 저장 중 오류: {e}")
        return {"status": "fail", "message": str(e)}



# =========================================================
# 통합 실행 함수
# =========================================================
def sync_all_forecast_stations(debug: bool = False):
    """단기 + 중기 예보 구역정보를 한 번에 동기화"""
    print("🚀 [SYNC] 단기 + 중기 예보 구역정보 전체 동기화 시작")

    result_short = sync_short_term_stations(debug)
    result_medium = sync_medium_term_stations(debug)

    print("\n✅ [완료 요약]")
    print(f" - 단기예보: {result_short.get('count', 0)}개 저장")
    print(f" - 중기예보: {result_medium.get('count', 0)}개 저장")

    return {
        "short_term": result_short,
        "medium_term": result_medium,
        "status": "success"
    }
