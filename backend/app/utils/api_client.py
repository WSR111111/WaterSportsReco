import requests
import time
import urllib3

# SSL 경고 억제 (개발 환경용)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_json(url: str, params: dict = None, retries: int = 3):
    """공통 GET 요청 함수 (재시도 포함)"""
    for attempt in range(retries):
        try:
            # SSL 검증 비활성화 및 세션 사용
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            # SSL 검증 비활성화 (개발 환경용)
            response = session.get(url, params=params, timeout=60, verify=False)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            if attempt == retries - 1:  # 마지막 시도
                print(f"최종 실패: {e}")
                raise e
            print(f"API 요청 실패 (시도 {attempt + 1}/{retries}), 5초 후 재시도...")
            time.sleep(5)

def get_text(url: str, params: dict = None, encoding: str = None):
    """텍스트 응답을 위한 GET 요청 함수"""
    response = requests.get(url, params=params, timeout=30)  # 30초 타임아웃
    response.raise_for_status()
    if encoding:
        response.encoding = encoding
    return response.text

def get_response(url: str, params: dict = None):
    """원시 응답 객체를 반환하는 GET 요청 함수"""
    response = requests.get(url, params=params, timeout=30)  # 30초 타임아웃
    response.raise_for_status()
    return response
