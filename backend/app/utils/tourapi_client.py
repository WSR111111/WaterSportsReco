from app.utils.api_client import get_json
from app.config import TOURIST_API_KEY

BASE_URL = "http://apis.data.go.kr/B551011/KorService2" 

def fetch_region(area_code: str = None):
    """지역 코드 전체 조회 (페이지네이션 포함)"""
    url = f"{BASE_URL}/ldongCode2"

    page_no = 1
    num_rows = 10  # 타임아웃 방지를 위해 작은 단위로 시작
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
            "lDongListYn": "Y"
        }
        if area_code:
            params["areaCode"] = area_code

        # 디버깅을 위한 URL 출력
        print(f"요청 URL: {url}")
        print(f"요청 파라미터: {params}")
        
        # 실제 요청 URL 확인
        import urllib.parse
        query_string = urllib.parse.urlencode(params)
        full_url = f"{url}?{query_string}"
        print(f"전체 URL: {full_url}")
        
        data = get_json(url, params)
        last_response = data  # 마지막 응답 저장

        body = data.get("response", {}).get("body", {})
        items = body.get("items", {}).get("item", [])

        if not items:
            break

        all_items.extend(items)

        total_count = body.get("totalCount", 0)
        # 다 가져왔으면 중단
        if page_no * num_rows >= total_count:
            break

        page_no += 1

    # 원래 API 구조 유지하면서 합쳐진 결과 리턴
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
