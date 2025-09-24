from app.utils.api_client import get_text
from app.config import KMA_API_KEY

BASE_URL = "https://apihub.kma.go.kr/api/typ01/url"

# 지상 관측 데이터
def fetch_surface_data(tm: str = None, stn: str = "0"):
    """
    tm: YYYYMMDDHHMM 형식 (ex: 202509141200), None이면 최신 데이터
    stn: 관측소 ID (기본=0 → 전체)
    """
    url = f"{BASE_URL}/kma_sfctm2.php"
    params = {"stn": stn, "authKey": KMA_API_KEY}
    if tm is not None:
        params["tm"] = tm
    return get_text(url, params, encoding='euc-kr')

# 해양 관측 데이터
def fetch_buoy_data(tm: str = None, stn: str = "0"):
    """
    tm: YYYYMMDDHHMM 형식 (ex: 202509141200), None이면 최신 데이터
    stn: 관측소 ID (기본=0 → 전체)
    """
    url = f"{BASE_URL}/kma_buoy.php"
    params = {"stn": stn, "authKey": KMA_API_KEY}
    if tm is not None:
        params["tm"] = tm
    return get_text(url, params, encoding='euc-kr')

# 지상 관측소 정보
def fetch_surface_stations(tm: str):
    url = f"{BASE_URL}/stn_inf.php"
    params = {"inf": "SFC", "tm": tm, "authKey": KMA_API_KEY}
    return get_text(url, params, encoding='euc-kr')

# 해양 관측소 정보
def fetch_buoy_stations(tm: str):
    url = f"{BASE_URL}/stn_inf.php"
    params = {"inf": "BUOY", "tm": tm, "authKey": KMA_API_KEY}
    return get_text(url, params, encoding='euc-kr')
