"""
app/services/code_sync_leisure.py
────────────────────────────────────────────
1. tourAPI 호출하여 leisure스포츠 시설, 상세정보 데이터 수집
2. API 원본 응답 (json/csv) 저장
3. 주요 필드 추출하여 CSV로 저장
4. CSV 읽어서 DB에 저장
"""

from app.database import DatabaseManager
from app.utils.tourapi_client import fetch_leisure_sports, fetch_place_detail
from app.services.csv_manager import CSVManager
from datetime import datetime

#=======================================================================
# leisure 시설 데이터
#=======================================================================

def sync_leisure_places(area_code: str = None, sigungu_code: str = None, num_rows: int = 1000, page_no: int = 1):

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_manager = CSVManager()
    
    try:
        # 1단계: TourAPI에서 fetch_leisure_sports()함수를 호출하여 모든 leisure 시설 데이터 수집
        print("=== 1단계: API 데이터 수집 ===")
        all_items = []
        page_no = 1
        
        while True:
            data = fetch_leisure_sports(area_code, sigungu_code, num_rows, page_no)
            body = data.get("response", {}).get("body", {})
            items = body.get("items", {}).get("item", [])
            
            if not items:
                break
                
            # 단일 아이템인 경우 리스트로 변환
            if isinstance(items, dict):
                items = [items]
                
            all_items.extend(items)
            
            # 전체 개수 확인
            total_count = body.get("totalCount", 0)
            if page_no * num_rows >= total_count:
                break
                
            page_no += 1
        
        print(f"API에서 수집된 레저시설 수: {len(all_items)}")
        
        # 2단계: 응답 원본(JSON)을 CSVManager.save_api_response()로 백업  
        print("=== 2단계: API 응답 백업 ===")
        csv_manager.save_api_response(data, "leisure_places", timestamp)
        
        # 3단계: 필요한 필드(content_id, title, addr1 등)만 추출하여 CSV 형태로 변환
        print("=== 3단계: CSV 데이터 변환 ===")
        csv_data = []
        for item in all_items:
            csv_row = {
                "content_id": int(item.get("contentid")),
                "category_code": item.get("cat3"),
                "place_name": item.get("title"),
                "address": item.get("addr1"),
                "address2": item.get("addr2"),
                "phone_number": item.get("tel"),
                "latitude": float(item["mapy"]) if item.get("mapy") else None,
                "longitude": float(item["mapx"]) if item.get("mapx") else None,
                "area_code": item.get("areacode"),
                "sigungu_code": item.get("sigungucode"),
                "first_image": item.get("firstimage"),
                "first_image2": item.get("firstimage2"),
                "created_at": timestamp
            }
            csv_data.append(csv_row)
        
        # 4단계: CSVManager.save_to_csv()로 CSV 파일 생성  
        print("=== 4단계: CSV 파일 저장 ===")
        csv_file_path = csv_manager.save_to_csv(csv_data, "leisure_places", timestamp)
        
        # 5단계: 생성된 CSV 파일 경로를 `save_leisure_csv_to_db()`로 넘겨 DB에 저장
        print("=== 5단계: DB 저장 ===")
        return save_leisure_csv_to_db(csv_file_path)
        
    except Exception as e:
        print(f"레저시설 동기화 실패: {e}")
        return {"status": "fail", "message": str(e)}


def _check_code_exists(db, code):
    """코드가 code 테이블에 존재하는지 확인"""
    try:
        result = db.execute_query("SELECT 1 FROM code WHERE code = %s", (code,))
        return len(result) > 0
    except:
        return False

# CSV를 직접 DB에 저장하는 함수
def save_leisure_csv_to_db(csv_file_path: str):

    db = DatabaseManager()
    if not db.connect():
        return {"status": "fail", "message": "DB 연결 실패"}
    

    # 기존 leisure_place 테이블 데이터 밀고 새로 불러온 데이터로 저장
    try:
        db.execute_non_query("DELETE FROM leisure_place")
        db.execute_non_query("ALTER SEQUENCE leisure_place_leisure_id_seq RESTART WITH 1")
        print("기존 데이터 삭제 및 ID 시퀀스 리셋 완료 (완전 교체 방식)")
    except Exception as e:
        print(f"데이터 삭제/리셋 중 오류: {e}")

    # csv 파일 로드
    try:
        csv_manager = CSVManager()
        items = csv_manager.load_from_csv(csv_file_path)
        
        count = 0
        for item in items:
            content_id = item.get("content_id")
            category_code = item.get("category_code")  # CSV 컬럼명에 맞게 수정
            place_name = item.get("place_name")
            address = item.get("address")
            address2 = item.get("address2")
            phone_number = item.get("phone_number")
            # latitude, longitude 처리 - 숫자가 아닌 값은 None으로 처리
            try:
                lat_value = item.get("latitude", "").strip()
                latitude = float(lat_value) if lat_value and lat_value != "None" and lat_value != "" else None
            except (ValueError, TypeError) as e:
                print(f"Latitude 변환 오류 - content_id: {content_id}, value: '{item.get('latitude')}', error: {e}")
                latitude = None
            
            try:
                lon_value = item.get("longitude", "").strip()
                longitude = float(lon_value) if lon_value and lon_value != "None" and lon_value != "" else None
            except (ValueError, TypeError) as e:
                print(f"Longitude 변환 오류 - content_id: {content_id}, value: '{item.get('longitude')}', error: {e}")
                longitude = None
            area_code_val = item.get("area_code")  # CSV 컬럼명에 맞게 수정
            first_image = item.get("first_image")
            first_image2 = item.get("first_image2")

            try:
                # 지역 정보는 이미 code 테이블에 있다고 가정하고 스킵
                # (필요시 별도로 지역 데이터 동기화 실행)

                # 스포츠 카테고리는 이미 code 테이블에 있다고 가정하고 스킵
                # (필요시 별도로 스포츠 카테고리 동기화 실행)

                # 레저 장소 저장
                query = """
                INSERT INTO leisure_place (cat_cd, content_id, place_name, address, address2,
                                           phone_number, latitude, longitude, reg_cd,
                                           first_image, first_image2)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (content_id) DO UPDATE SET
                    cat_cd=EXCLUDED.cat_cd,
                    place_name=EXCLUDED.place_name,
                    address=EXCLUDED.address,
                    address2=EXCLUDED.address2,
                    phone_number=EXCLUDED.phone_number,
                    latitude=EXCLUDED.latitude,
                    longitude=EXCLUDED.longitude,
                    reg_cd=EXCLUDED.reg_cd,
                    first_image=EXCLUDED.first_image,
                    first_image2=EXCLUDED.first_image2
                """
                db.execute_non_query(query, (
                    category_code, content_id, place_name, address, address2, phone_number,
                    latitude, longitude, area_code_val, first_image, first_image2
                ))
                count += 1
                
            except Exception as e:
                print(f"레저 장소 저장 실패: {content_id}, cat_cd: {category_code}, reg_cd: {area_code_val}, Error: {e}")
                continue

        return {"status": "success", "count": count, "csv_file": csv_file_path}

    except Exception as e:
        return {"status": "fail", "message": str(e)}

    finally:
        db.disconnect()


#=======================================================================
# leisure 시설 상세정보 데이터
#=======================================================================

def sync_place_details():
    """leisure_place에 등록된 content_id 기준으로 상세정보를 가져와 CSV로 저장한 후 DB 저장"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_manager = CSVManager()
    
    db = DatabaseManager()
    if not db.connect():
        return {"status": "fail", "message": "DB 연결 실패"}

    try:
        # 1단계: content_id 목록 조회
        print("=== 1단계: content_id 목록 조회 ===")
        content_ids_result = db.execute_query("SELECT content_id FROM leisure_place")
        content_ids = [int(row["content_id"]) for row in content_ids_result]
        print(f"조회할 content_id 수: {len(content_ids)}")
        
        # 2단계: API에서 상세정보 수집
        print("=== 2단계: API 상세정보 수집 ===")
        csv_data = []
        api_responses = []
        
        for content_id in content_ids:
            try:
                data = fetch_place_detail(content_id)
                api_responses.append({"content_id": content_id, "response": data})
                
                items = data.get("response", {}).get("body", {}).get("items", {}).get("item", [])
                if not items:
                    continue

                item = items[0]
                csv_row = {
                    "content_id": content_id,
                    "homepage": item.get("homepage"),
                    "overview": item.get("overview"),
                    "created_at": timestamp
                }
                csv_data.append(csv_row)
                
            except Exception as e:
                print(f"상세정보 조회 실패 - content_id: {content_id}, Error: {e}")
                continue
        
        print(f"수집된 상세정보 수: {len(csv_data)}")
        
        # 3단계: API 응답 백업
        print("=== 3단계: API 응답 백업 ===")
        csv_manager.save_api_response(api_responses, "place_details", timestamp)
        
        # 4단계: CSV 파일로 저장
        print("=== 4단계: CSV 파일 저장 ===")
        if csv_data:
            csv_file_path = csv_manager.save_to_csv(csv_data, "place_details", timestamp)
            
            # 5단계: CSV에서 읽어서 DB에 저장
            print("=== 5단계: DB 저장 ===")
            return save_place_details_csv_to_db(csv_file_path)
        else:
            return {"status": "success", "count": 0, "message": "저장할 상세정보가 없습니다"}

    except Exception as e:
        return {"status": "fail", "message": str(e)}

    finally:
        db.disconnect()


def save_place_details_csv_to_db(csv_file_path: str):
    """CSV 파일에서 장소 상세정보를 읽어 DB에 저장"""
    db = DatabaseManager()
    if not db.connect():
        return {"status": "fail", "message": "DB 연결 실패"}

    try:
        csv_manager = CSVManager()
        items = csv_manager.load_from_csv(csv_file_path)
        
        count = 0
        for item in items:
            content_id = int(item.get("content_id"))
            homepage = item.get("homepage")
            overview = item.get("overview")

            query = """
            INSERT INTO leisure_place_detail (content_id, homepage, overview)
            VALUES (%s,%s,%s)
            """
            db.execute_non_query(query, (content_id, homepage, overview))
            count += 1

        return {"status": "success", "count": count, "csv_file": csv_file_path}

    except Exception as e:
        return {"status": "fail", "message": str(e)}

    finally:
        db.disconnect()
