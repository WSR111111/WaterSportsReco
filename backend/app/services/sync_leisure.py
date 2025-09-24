from app.db.database import DatabaseManager
from app.utils.tourapi_client import fetch_leisure_sports, fetch_place_detail


def sync_leisure_places(area_code: str = None, sigungu_code: str = None, num_rows: int = 1000, page_no: int = 1):
    """레저스포츠 시설 목록을 가져와 DB에 저장"""
    db = DatabaseManager()
    if not db.connect():
        return {"status": "fail", "message": "DB 연결 실패"}

    try:
        # 페이지네이션으로 전체 데이터 수집
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
        
        items = all_items
        
        count = 0
        for item in items:
            content_id = str(item.get("contentid"))
            category_code = item.get("cat3")
            place_name = item.get("title")
            address = item.get("addr1")
            address2 = item.get("addr2")
            phone_number = item.get("tel")
            latitude = float(item["mapy"]) if item.get("mapy") else None
            longitude = float(item["mapx"]) if item.get("mapx") else None
            area_code_val = item.get("areacode")
            sigungu_code_val = item.get("sigungucode")
            first_image = item.get("firstimage")
            first_image2 = item.get("firstimage2")

            try:
                # 지역 정보가 없으면 자동 생성
                if sigungu_code_val:
                    region_check_query = "SELECT COUNT(*) FROM region WHERE lDongSignguCd = %s"
                    region_exists = db.execute_query(region_check_query, (sigungu_code_val,))
                    
                    if region_exists[0][0] == 0:
                        # 지역 정보가 없으면 기본값으로 생성
                        insert_region_query = """
                        INSERT INTO region (lDongRegnCd, lDongSignguCd, lDongRegnNm, lDongSignguNm)
                        VALUES (%s, %s, %s, %s)
                        """
                        db.execute_non_query(insert_region_query, (
                            area_code_val or "00",
                            sigungu_code_val,
                            f"Area_{area_code_val}" if area_code_val else "Unknown_Area",
                            f"Sigungu_{sigungu_code_val}"
                        ))

                # 스포츠 카테고리가 없으면 자동 생성
                if category_code:
                    sports_check_query = "SELECT COUNT(*) FROM sports WHERE category_code = %s"
                    sports_exists = db.execute_query(sports_check_query, (category_code,))
                    
                    if sports_exists[0][0] == 0:
                        # 스포츠 카테고리가 없으면 기본값으로 생성
                        insert_sports_query = """
                        INSERT INTO sports (category_code, sport_name)
                        VALUES (%s, %s)
                        """
                        db.execute_non_query(insert_sports_query, (
                            category_code,
                            f"Sport_{category_code}"
                        ))

                # 레저 장소 저장
                query = """
                INSERT INTO leisure_place (category_code, content_id, place_name, address, address2,
                                           phone_number, latitude, longitude, lDongRegnCd, lDongSignguCd,
                                           first_image, first_image2)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON DUPLICATE KEY UPDATE
                    category_code=VALUES(category_code),
                    place_name=VALUES(place_name),
                    address=VALUES(address),
                    address2=VALUES(address2),
                    phone_number=VALUES(phone_number),
                    latitude=VALUES(latitude),
                    longitude=VALUES(longitude),
                    lDongRegnCd=VALUES(lDongRegnCd),
                    lDongSignguCd=VALUES(lDongSignguCd),
                    first_image=VALUES(first_image),
                    first_image2=VALUES(first_image2)
                """
                db.execute_non_query(query, (
                    category_code, content_id, place_name, address, address2, phone_number,
                    latitude, longitude, area_code_val, sigungu_code_val, first_image, first_image2
                ))
                count += 1
                
            except Exception as e:
                print(f"레저 장소 저장 실패: {content_id}, Error: {e}")
                continue

        return {"status": "success", "count": count}

    except Exception as e:
        return {"status": "fail", "message": str(e)}

    finally:
        db.disconnect()


def sync_place_details():
    """leisure_place에 등록된 content_id 기준으로 상세정보를 가져와 DB 저장"""
    db = DatabaseManager()
    if not db.connect():
        return {"status": "fail", "message": "DB 연결 실패"}

    try:
        # content_id 목록 조회
        content_ids_result = db.execute_query("SELECT content_id FROM leisure_place")
        content_ids = [row[0] for row in content_ids_result]

        count = 0
        for content_id in content_ids:
            data = fetch_place_detail(content_id)
            items = data.get("response", {}).get("body", {}).get("items", {}).get("item", [])
            if not items:
                continue

            item = items[0]
            homepage = item.get("homepage")
            overview = item.get("overview")

            query = """
            INSERT INTO place_detail (content_id, homepage, overview)
            VALUES (%s,%s,%s)
            ON DUPLICATE KEY UPDATE
                homepage=VALUES(homepage),
                overview=VALUES(overview)
            """
            db.execute_non_query(query, (content_id, homepage, overview))
            count += 1

        return {"status": "success", "count": count}

    except Exception as e:
        return {"status": "fail", "message": str(e)}

    finally:
        db.disconnect()
