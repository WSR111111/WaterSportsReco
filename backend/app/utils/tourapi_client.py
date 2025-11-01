"""
app/utils/tourapi_client.py
────────────────────────────────────────────
- 한국관공사 TourAPI 데이터 수집
1. 지역 코드
2. 수상스포츠 카테고리 조회
3. 수상스포츠 시설 목록 조회
4. 수상스포츠 시설 상세정보 조회
"""

from app.utils.api_client import get_json
from app.config import TOURIST_API_KEY

# Tour API 기본 엔드포인트(URL)
BASE_URL = "http://apis.data.go.kr/B551011/KorService2" 

def fetch_region(area_code: str = None):
    """
    지역 코드 전체 조회 (시·도 및 시군구)
    areaCode가 None이면 전국 시·도 리스트,
    areaCode 지정 시 해당 지역의 시군구 리스트 반환
    """
    url = f"{BASE_URL}/areaCode2"

    page_no = 1
    num_rows = 50
    all_items = []
    last_response = None

    while True:
        params = {
            "serviceKey": TOURIST_API_KEY,
            "numOfRows": num_rows,
            "pageNo": page_no,
            "MobileOS": "ETC",
            "MobileApp": "APP",
            "_type": "json",
        }
        if area_code:
            params["areaCode"] = area_code

        print(f"요청 URL: {url}")
        print(f"요청 파라미터: {params}")

        import urllib.parse
        query_string = urllib.parse.urlencode(params)
        print(f"전체 URL: {url}?{query_string}")

        data = get_json(url, params)
        last_response = data

        body = data.get("response", {}).get("body", {})
        items = body.get("items", {}).get("item", [])

        if not items:
            break

        # 하위 지역도 코드에 prefix 붙여 구분
        for item in items:
            if area_code:
                item["upperCode"] = f"reg{int(area_code):02d}"  # 예: reg01
                item["fullCode"] = f"{item['upperCode']}{int(item['code']):02d}"  # 예: reg0101
            else:
                item["upperCode"] = "reg"
                item["fullCode"] = f"reg{int(item['code']):02d}"

        all_items.extend(items)

        total_count = body.get("totalCount", 0)
        if page_no * num_rows >= total_count:
            break
        page_no += 1

    if last_response:
        last_response["response"]["body"]["items"]["item"] = all_items
        last_response["response"]["body"]["numOfRows"] = len(all_items)
        last_response["response"]["body"]["totalCount"] = len(all_items)

    return last_response



# 스포츠 카테고리 조회 
def fetch_sports(cat1="A03", cat2="A0303"):
    """
    수상레저스포츠의 세부 카테고리(cat3) 조회
    cat1=A03: 레저스포츠
    cat2=A0303: 수상레저스포츠
    """
    url = f"{BASE_URL}/categoryCode2"
    params = {
        "serviceKey": TOURIST_API_KEY,
        "numOfRows": 10,  
        "pageNo": 1,
        "MobileOS": "ETC",
        "MobileApp": "APP",
        "cat1": cat1,
        "cat2": cat2,
        "_type": "json"
    }
    return get_json(url, params)

# 레저스포츠 시설 목록 조회
def fetch_leisure_sports(area_code: str = None, sigungu_code: str = None, num_rows: int = 10, page_no: int = 1):
    """
    레저스포츠 시설 목록을 조회합니다.
    contentTypeId=28: 레저스포츠
    cat1=A03, cat2=A0303: 레저스포츠 > 수상레저스포츠
    """
    url = f"{BASE_URL}/areaBasedList2"
    params = {
        "serviceKey": TOURIST_API_KEY,
        "numOfRows": num_rows,
        "pageNo": page_no,
        "MobileOS": "ETC",
        "MobileApp": "AppTest",
        "_type": "json",
        "arrange": "A",
        "contentTypeId": 28,
        "cat1": "A03",
        "cat2": "A0303"
    }
    if area_code:
        params["areaCode"] = area_code
    if sigungu_code:
        params["sigunguCode"] = sigungu_code
    return get_json(url, params)

# 레저스포츠 시설 상세 조회
def fetch_place_detail(content_id: str):
    url = f"{BASE_URL}/detailCommon2"
    params = {
        "serviceKey": TOURIST_API_KEY,
        "MobileOS": "ETC",
        "MobileApp": "AppTest",
        "_type": "json",
        "contentId": content_id,
        "numOfRows": 10,
        "pageNo": 1
    }
    return get_json(url, params)
