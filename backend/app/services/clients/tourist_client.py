from typing import Dict, Any, List, Optional
import httpx
import json
from ...config import TOURIST_API_KEY


def _parse_leisure_places_json(response_text: str) -> List[Dict[str, Any]]:
    """JSON 응답을 파싱하여 레저 장소 정보를 반환"""
    try:
        data = json.loads(response_text)
        
        response = data.get('response', {})
        header = response.get('header', {})
        
        # 응답 상태 확인
        result_code = header.get('resultCode', '')
        if result_code != '0000':
            result_msg = header.get('resultMsg', 'Unknown error')
            print(f"❌ API Error: {result_code} - {result_msg}")
            return []
        
        # 데이터 추출
        body = response.get('body', {})
        items = body.get('items', {})
        
        # item이 리스트인지 단일 객체인지 확인
        item_data = items.get('item', [])
        if isinstance(item_data, dict):
            item_data = [item_data]
        elif not isinstance(item_data, list):
            item_data = []
        
        leisure_places = []
        for item in item_data:
            try:
                # 위경도 변환
                lat = None
                lon = None
                if item.get('mapy'):
                    try:
                        lat = float(item['mapy'])
                    except (ValueError, TypeError):
                        pass
                if item.get('mapx'):
                    try:
                        lon = float(item['mapx'])
                    except (ValueError, TypeError):
                        pass
                
                place = {
                    "content_id": item.get('contentid', ''),
                    "title": item.get('title', ''),
                    "addr1": item.get('addr1', ''),
                    "addr2": item.get('addr2', ''),
                    "mapy": lat,
                    "mapx": lon,
                    "tel": item.get('tel', ''),
                    "areacode": item.get('areacode', ''),
                    "sigungucode": item.get('lDongSignguCd', ''), 
                    "cat3": item.get('cat3', ''),
                    "firstimage": item.get('firstimage', ''),
                    "firstimage2": item.get('firstimage2', ''),
                    "source": "TOURIST"
                }
                
                # 유효한 위경도가 있는 경우만 포함
                if lat is not None and lon is not None:
                    leisure_places.append(place)
                    
            except Exception as e:
                print(f"❌ Error parsing leisure place item: {e}")
                continue
        
        print(f"✅ Parsed {len(leisure_places)} leisure places from API response")
        return leisure_places
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        return []
    except Exception as e:
        print(f"❌ Unexpected error in leisure places parsing: {e}")
        return []


async def fetch_leisure_places_json(
    client: httpx.AsyncClient,
    area_code: Optional[str] = None,
    sigungu_code: Optional[str] = None,
    content_type_id: str = "28",
    cat1: str = "A03",
    cat2: str = "A0303",
    cat3: Optional[str] = None,
    num_of_rows: int = 1000,
    page_no: int = 1,
    arrange: str = "C"
) -> List[Dict[str, Any]]:
    """레저 장소 정보를 JSON으로 가져옴"""
    url = "https://apis.data.go.kr/B551011/KorService2/areaBasedList2"
    
    params = {
        "serviceKey": TOURIST_API_KEY,
        "numOfRows": num_of_rows,
        "pageNo": page_no,
        "MobileOS": "ETC",
        "MobileApp": "AppTest",
        "contentTypeId": content_type_id,
        "cat1": cat1,
        "cat2": cat2,
        "arrange": arrange,
        "_type": "json"
    }
    
    if cat3:
        params["cat3"] = cat3
    if area_code:
        params["areaCode"] = area_code
    if sigungu_code:
        params["sigunguCode"] = sigungu_code
    
    try:
        print(f"🔍 Fetching leisure places from API...")
        
        response = await client.get(url, params=params, timeout=30.0)
        response.raise_for_status()
        
        print(f"✅ API response received (status: {response.status_code})")
        
        # JSON 응답 파싱
        leisure_places = _parse_leisure_places_json(response.text)
        
        if not leisure_places:
            print("⚠️ No leisure places found in API response")
            return []
        
        print(f"✅ Successfully fetched {len(leisure_places)} leisure places")
        return leisure_places
        
    except httpx.TimeoutException:
        print("❌ API request timeout (30 seconds)")
        return []
    except httpx.HTTPStatusError as e:
        print(f"❌ HTTP error {e.response.status_code}: {e.response.text}")
        return []
    except httpx.RequestError as e:
        print(f"❌ Network error: {e}")
        return []
    except Exception as e:
        print(f"❌ Unexpected error fetching leisure places: {e}")
        return []


def _parse_detail_common2_json(response_text: str) -> Dict[str, Any]:
    """detailCommon2 JSON 응답을 파싱하여 상세 정보를 반환"""
    try:
        data = json.loads(response_text)
        
        response = data.get('response', {})
        header = response.get('header', {})
        
        # 응답 상태 확인
        result_code = header.get('resultCode', '')
        if result_code != '0000':
            result_msg = header.get('resultMsg', 'Unknown error')
            print(f"❌ API Error: {result_code} - {result_msg}")
            return {}
        
        # 데이터 추출
        body = response.get('body', {})
        items = body.get('items', {})
        
        # item이 리스트인지 단일 객체인지 확인
        item_data = items.get('item', {})
        if isinstance(item_data, list) and len(item_data) > 0:
            item_data = item_data[0]
        elif not isinstance(item_data, dict):
            return {}
        
        # detailCommon2 API는 일반적인 상세 정보를 제공
        detail = {
            "contentid": item_data.get('contentid', ''),
            "homepage": item_data.get('homepage', ''),
            "overview": item_data.get('overview', ''),
            "title": item_data.get('title', ''),
            "addr1": item_data.get('addr1', ''),
            "addr2": item_data.get('addr2', ''),
            "tel": item_data.get('tel', ''),
            "firstimage": item_data.get('firstimage', ''),
            "firstimage2": item_data.get('firstimage2', ''),
            "zipcode": item_data.get('zipcode', ''),
            "mapx": item_data.get('mapx', ''),
            "mapy": item_data.get('mapy', ''),
            "mlevel": item_data.get('mlevel', ''),
            "booktour": item_data.get('booktour', ''),
        }
        
        return detail
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        return {}
    except Exception as e:
        print(f"❌ Unexpected error in detail parsing: {e}")
        return {}


async def fetch_detail_common_json(
    client: httpx.AsyncClient,
    content_id: str
) -> Dict[str, Any]:
    """특정 콘텐츠의 상세 정보를 JSON으로 가져옴"""
    url = "https://apis.data.go.kr/B551011/KorService2/detailCommon2"
    
    params = {
        "serviceKey": TOURIST_API_KEY,
        "MobileOS": "ETC",
        "MobileApp": "AppTest",
        "_type": "json",
        "contentId": content_id,
        "numOfRows": 10,
        "pageNo": 1
    }
    
    try:
        response = await client.get(url, params=params, timeout=15.0)
        response.raise_for_status()
        
        # XML 에러 응답 체크 (API 한도 초과 등)
        if response.text.startswith('<OpenAPI_ServiceResponse>'):
            if 'APPLICATION_ERROR' in response.text:
                print(f"⚠️ Content not available for content_id {content_id} (APPLICATION_ERROR)")
            elif 'LIMITED_NUMBER_OF_SERVICE_REQUESTS_EXCEEDS_ERROR' in response.text:
                print(f"❌ API limit exceeded for content_id {content_id}")
            else:
                print(f"❌ API Service Error for content_id {content_id}")
            return {}
        
        # JSON 응답 파싱
        detail = _parse_detail_common2_json(response.text)
        
        if not detail:
            print(f"⚠️ No detail found for content_id: {content_id}")
            return {}
        
        return detail
        
    except httpx.TimeoutException:
        print(f"❌ API request timeout for content_id: {content_id}")
        return {}
    except httpx.HTTPStatusError as e:
        print(f"❌ HTTP error {e.response.status_code} for content_id {content_id}: {e.response.text[:200]}...")
        return {}
    except httpx.RequestError as e:
        print(f"❌ Network error for content_id {content_id}: {e}")
        return {}
    except Exception as e:
        print(f"❌ Unexpected error fetching detail for content_id {content_id}: {e}")
        return {}


def _parse_category_data(response_text: str) -> List[Dict[str, Any]]:
    """
    JSON 응답을 파싱하여 카테고리 정보를 반환
    """
    try:
        data = json.loads(response_text)
        
        # API 응답 구조 확인
        response = data.get('response', {})
        header = response.get('header', {})
        
        # 응답 상태 확인
        result_code = header.get('resultCode', '')
        if result_code != '0000':
            result_msg = header.get('resultMsg', 'Unknown error')
            print(f"❌ API Error: {result_code} - {result_msg}")
            return []
        
        # 데이터 추출
        body = response.get('body', {})
        items = body.get('items', {})
        
        # item이 리스트인지 단일 객체인지 확인
        item_data = items.get('item', [])
        if isinstance(item_data, dict):
            item_data = [item_data]
        elif not isinstance(item_data, list):
            item_data = []
        
        categories = []
        for item in item_data:
            try:
                category = {
                    "code": item.get('code', ''),
                    "name": item.get('name', ''),
                    "rnum": item.get('rnum', 0)
                }
                
                # 필수 필드 검증
                if category["code"] and category["name"]:
                    categories.append(category)
                else:
                    print(f"⚠️ Skipping invalid category: {item}")
                    
            except Exception as e:
                print(f"❌ Error parsing category item: {e}")
                continue
        
        print(f"✅ Parsed {len(categories)} categories from API response")
        return categories
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        return []
    except Exception as e:
        print(f"❌ Unexpected error in category data parsing: {e}")
        return []


async def fetch_category_codes(
    client: httpx.AsyncClient,
    content_type_id: str = "28",
    cat1: str = "A03", 
    cat2: str = "A0303",
    num_of_rows: int = 100,
    page_no: int = 1
) -> List[Dict[str, Any]]:
    """
    한국관광공사 카테고리 코드 API를 호출하여 카테고리 정보를 가져옴
    """
    url = "https://apis.data.go.kr/B551011/KorService2/categoryCode2"
    
    params = {
        "serviceKey": TOURIST_API_KEY,
        "numOfRows": num_of_rows,
        "pageNo": page_no,
        "MobileOS": "ETC",
        "MobileApp": "AppTest",
        "contentTypeId": content_type_id,
        "cat1": cat1,
        "cat2": cat2,
        "_type": "json"
    }
    
    try:
        print(f"🔍 Fetching category codes from API...")
        
        response = await client.get(url, params=params, timeout=30.0)
        response.raise_for_status()
        
        print(f"✅ API response received (status: {response.status_code})")
        
        # JSON 응답 파싱
        categories = _parse_category_data(response.text)
        
        if not categories:
            print("⚠️ No categories found in API response")
            return []
        
        print(f"✅ Successfully fetched {len(categories)} categories")
        return categories
        
    except httpx.TimeoutException:
        print("❌ API request timeout (30 seconds)")
        return []
    except httpx.HTTPStatusError as e:
        print(f"❌ HTTP error {e.response.status_code}: {e.response.text}")
        return []
    except httpx.RequestError as e:
        print(f"❌ Network error: {e}")
        return []
    except Exception as e:
        print(f"❌ Unexpected error fetching categories: {e}")
        return []