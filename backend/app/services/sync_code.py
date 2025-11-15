"""
app/services/sync_code.py
────────────────────────────────────────────
🧩 코드 테이블 통합 동기화 서비스

이 모듈은 TourAPI로부터 지역(region) 코드, 스포츠(sports) 카테고리 코드,
또는 일반 코드(code) CSV 파일을 불러와 PostgreSQL의 code 테이블에 저장/갱신하는 기능을 제공한다.

[지원 기능]
- sync_code_from_csv() : 기존 code.csv 파일을 DB에 반영
- sync_code_from_api(code_type): region / sports API 호출 → CSV 저장 → code 테이블 저장
- sync_all_codes(): region + sports + code 파일을 한 번에 전체 동기화
"""

from app.utils.tourapi_client import fetch_region, fetch_sports
from app.database import DatabaseManager
from app.services.csv_manager import CSVManager
from datetime import datetime


# ------------------------------------------------------------
# ✅ 공통: CSV 파일을 DB(code 테이블)에 저장
# ------------------------------------------------------------
def _save_code_csv_to_db(csv_file_path: str):
    """CSV 파일을 읽어 code 테이블에 삽입/갱신"""
    db = DatabaseManager()

    try:
        csv_manager = CSVManager()
        items = csv_manager.load_from_csv(csv_file_path)

        count = 0
        for item in items:
            code = item.get("code")
            code_desc = item.get("code_desc")
            code_name = item.get("code_name")
            upper_code = item.get("upper_code")

            if not code or not code_name:
                print(f"⚠️ 필수 필드 누락: {item}")
                continue

            query = """
            INSERT INTO code (code, code_desc, code_name, upper_code)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (code) DO UPDATE SET
                code_desc = EXCLUDED.code_desc,
                code_name = EXCLUDED.code_name,
                upper_code = EXCLUDED.upper_code;
            """
            db.execute_non_query(query, (code, code_desc, code_name, upper_code))
            count += 1

        print(f"✅ {count}개의 코드가 DB에 저장/갱신되었습니다.")
        return {"status": "success", "count": count, "csv_file": csv_file_path}

    except Exception as e:
        print(f"❌ DB 저장 중 오류: {e}")
        return {"status": "fail", "message": str(e)}

    finally:
        db.disconnect()


# ------------------------------------------------------------
# ✅ 기존 CSV 파일에서 code 테이블 동기화
# ------------------------------------------------------------
def sync_code_from_csv(csv_file_path: str = None):
    """기존 CSV(code_*.csv) 파일을 DB에 반영"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_manager = CSVManager()

    try:
        if csv_file_path is None:
            csv_file_path = csv_manager.get_latest_csv("code")

        print(f"\n=== 코드 테이블 CSV → DB 저장 ===")
        print(f"📁 CSV 파일: {csv_file_path}")

        return _save_code_csv_to_db(csv_file_path)

    except Exception as e:
        return {"status": "fail", "message": str(e)}


# ------------------------------------------------------------
# ✅ TourAPI 호출을 통한 코드 데이터 동기화 (region / sports)
# ------------------------------------------------------------
def sync_code_from_api(code_type: str):
    """
    TourAPI에서 region 또는 sports 코드 데이터를 가져와
    CSV로 저장하고 code 테이블에 반영
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_manager = CSVManager()
    db = DatabaseManager()

    try:
        print(f"\n=== {code_type.upper()} 코드 API 데이터 수집 시작 ===")

        # 1️⃣ API 데이터 호출
        if code_type == "region":
            data = fetch_region()
        elif code_type == "sports":
            data = fetch_sports()
        else:
            raise ValueError(f"지원하지 않는 code_type: {code_type}")

        print("✅ API 응답 수신 완료")

        # 2️⃣ 응답 백업 저장 (JSON)
        csv_manager.save_api_response(data, f"code_{code_type}", timestamp)

        # 3️⃣ CSV 변환
        items = data["response"]["body"]["items"]["item"]
        csv_data = []

        if code_type == "region":
            for item in items:
                if not item.get("code") or not item.get("name"):
                    continue
                csv_data.append({
                    "code": item.get("fullCode"),         # 위에서 생성한 fullCode (reg01, reg0101 등)
                    "code_desc": "reg_cd",
                    "code_name": item.get("name"),
                    "upper_code": item.get("upperCode"),  # 상위 지역 연결
                    "created_at": timestamp
                })


        elif code_type == "sports":
            for item in items:
                if not item.get("code") or not item.get("name"):
                    continue
                csv_data.append({
                    "code": item.get("code"),
                    "code_desc": "cat_cd",
                    "code_name": item.get("name"),
                    "upper_code": "cat",
                    "created_at": timestamp
                })

        print(f"✅ 변환된 {code_type} 코드 데이터 수: {len(csv_data)}")

        # 4️⃣ CSV 파일 저장
        csv_file_path = csv_manager.save_to_csv(csv_data, f"code_{code_type}", timestamp)

        # 5️⃣ DB 저장
        return _save_code_csv_to_db(csv_file_path)

    except Exception as e:
        print(f"❌ {code_type} 코드 동기화 실패: {e}")
        return {"status": "fail", "message": str(e)}

    finally:
        db.disconnect()


# ------------------------------------------------------------
# ✅ region + sports + code 전체 통합 동기화
# ------------------------------------------------------------
def sync_all_codes():
    """지역(region), 스포츠(sports), code CSV를 모두 DB에 반영"""
    csv_manager = CSVManager()
    results = []

    try:
        print("\n=== 전체 코드 통합 동기화 시작 ===")

        # 1️⃣ region 코드 API → CSV → DB
        region_result = sync_code_from_api("region")
        results.append({"type": "region", **region_result})

        # 2️⃣ sports 코드 API → CSV → DB
        sports_result = sync_code_from_api("sports")
        results.append({"type": "sports", **sports_result})

        # 3️⃣ 기존 code.csv 파일 → DB
        try:
            latest_code_csv = csv_manager.get_latest_csv("code")
            code_result = _save_code_csv_to_db(latest_code_csv)
            results.append({"type": "code_csv", **code_result})
        except FileNotFoundError:
            print("⚠️ code.csv 파일이 없어 건너뜀")

        total_success = sum(r.get("count", 0) for r in results if r["status"] == "success")
        print(f"\n✅ 전체 코드 통합 동기화 완료: 총 {total_success}건 반영")

        return {"status": "success", "total_count": total_success, "details": results}

    except Exception as e:
        print(f"❌ 전체 코드 통합 동기화 중 오류: {e}")
        return {"status": "fail", "message": str(e)}
