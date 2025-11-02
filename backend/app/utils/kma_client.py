"""
app/utils/kma_client.py
────────────────────────────────────────────
- 기상청API를 통해 지상/해양 관측 및 관측소 데이터 불러오기
"""
from datetime import datetime, timedelta
from app.utils.api_client import get_text
from app.config import KMA_API_KEY

# 기상청 API 기본 엔드포인트(URL)
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
def fetch_surface_stations(tm: str = None):
    """
    지상 관측소 정보 조회
    tm: YYYYMMDDHHMM 형식 (생략 시 최신 데이터 자동 반환)
    """
    url = f"{BASE_URL}/stn_inf.php"
    params = {"inf": "SFC", "authKey": KMA_API_KEY}
    if tm is not None:
        params["tm"] = tm  # ✅ tm이 주어졌을 때만 추가
    return get_text(url, params, encoding='euc-kr')

# 해양 관측소 정보
def fetch_buoy_stations(tm: str = None):
    """
    해양 관측소 정보 조회
    tm: YYYYMMDDHHMM 형식 (생략 시 최신 데이터 자동 반환)
    """
    url = f"{BASE_URL}/stn_inf.php"
    params = {"inf": "BUOY", "authKey": KMA_API_KEY}
    if tm is not None:
        params["tm"] = tm  # ✅ tm이 주어졌을 때만 추가
    return get_text(url, params, encoding='euc-kr')


#=================================================================
# 단기예보
#=================================================================
def fetch_short_term_station(reg: str = "", disp: int = 0, help: int = 0):
    """
    단기예보 구역정보 조회
    reg : 예보구역코드 (비워두면 전체)
    disp : 출력형식 (0=기본, 1=구분자형)
    help : 1이면 컬럼명 출력

    ※ 단기예보 구역 정보는 시간 파라미터(tmfc 등)가 필요 없음.
    항상 최신 구역정보를 반환함.
    """
    url = f"{BASE_URL}/fct_shrt_reg.php"
    params = {
        "reg": reg or "",     # None 방지
        "disp": disp,
        "help": help,
        "authKey": KMA_API_KEY,
    }

    print(f"📡 [KMA] 단기예보 구역정보 요청 (reg={reg or 'ALL'})")
    return get_text(url, params, encoding="euc-kr")



def fetch_land_forecast(reg: str = "", disp: int = 0, help: int = 0):
    """
    육상 단기예보 데이터 조회
    reg: 예보구역코드 (비워두면 전체)
    disp: 출력형식 (0=기본, 1=구분자형)
    help: 1이면 컬럼명 출력
    ※ 육상예보는 tmfc 생략 시 자동으로 최신 발표시각 반환
    """
    url = f"{BASE_URL}/fct_afs_dl.php"
    params = {
        "reg": reg,
        "disp": disp,
        "help": help,
        "authKey": KMA_API_KEY,
    }
    return get_text(url, params, encoding="euc-kr")


def fetch_marine_forecast(reg: str = "", disp: int = 0, help: int = 0):
    """
    해상 단기예보 데이터 조회 (자동 시간 구간 계산)
    reg: 예보구역코드 (비워두면 전체)
    disp: 출력형식 (0=기본, 1=구분자형)
    help: 1이면 컬럼명 출력

    ※ tmfc1~tmfc2를 생략해도 현재시각 기준으로
    최근 발표시각 ~ 3일 후 발표시각까지 자동 계산됨
    """
    url = f"{BASE_URL}/fct_afs_do.php"
    
    # 단기 해상예보 발표시각 (일 8회)
    RELEASE_HOURS = [2, 5, 8, 11, 14, 17, 20, 23]
    now = datetime.now()

    # ✅ 현재 시각보다 작거나 같은 발표시각 중 가장 최근 시각 찾기
    latest_hour = max([h for h in RELEASE_HOURS if h <= now.hour], default=23)

    # 0~1시 사이라면 전날 23시 발표 사용
    if now.hour < 2:
        now -= timedelta(days=1)

    # 시작 발표시각 (tmfc1)
    tmfc1 = now.replace(hour=latest_hour, minute=0, second=0, microsecond=0)

    # 종료 발표시각 (tmfc2) → 3일 후 +1시간 정도 여유
    tmfc2 = tmfc1 + timedelta(days=3, hours=1)

    tmfc1_str = tmfc1.strftime("%Y%m%d%H")
    tmfc2_str = tmfc2.strftime("%Y%m%d%H")

    params = {
        "reg": reg,
        "tmfc1": tmfc1_str,
        "tmfc2": tmfc2_str,
        "disp": disp,
        "help": help,
        "authKey": KMA_API_KEY,
    }

    print(f"📡 [KMA] 해상예보 요청 tmfc1={tmfc1_str}, tmfc2={tmfc2_str}")
    return get_text(url, params, encoding="euc-kr")


#=================================================================
# 중기예보
#=================================================================
def fetch_medium_term_station(reg: str = "", disp: int = 0, help: int = 0):
    """
    중기예보 구역정보 조회
    reg : 예보구역코드 (비워두면 전체)
    disp : 출력형식 (0=기본, 1=구분자형)
    help : 1이면 컬럼명 출력

    ※ 중기예보 구역 정보는 시간 파라미터(tmfc 등)가 필요 없음.
    항상 최신 구역정보를 반환함.
    """
    url = f"{BASE_URL}/fct_medm_reg.php"
    params = {
        "reg": reg or "",
        "disp": disp,
        "help": help,
        "authKey": KMA_API_KEY,
    }

    print(f"📡 [KMA] 중기예보 구역정보 요청 (reg={reg or 'ALL'})")
    return get_text(url, params, encoding="euc-kr")


def fetch_medium_land_forecast(reg: str = "", disp: int = 0, help: int = 0,
                            tmfc1: str = "", tmfc2: str = "", tmef1: str = "", tmef2: str = ""):
    """
    중기 육상예보 조회
    reg   : 예보구역코드 (비워두면 전체)
    disp  : 출력형식 (0=기본, 1=구분자형)
    help  : 1이면 컬럼명 출력
    tmfc1~2 : 발표시각 범위 (YYYYMMDDHH, 생략 가능)
    tmef1~2 : 발효시각 범위 (YYYYMMDDHH, 생략 가능)
    
    ※ 중기예보는 단기와 달리 tmfc1~tmfc2, tmef1~tmef2를 지정하지 않아도 최신 데이터 반환.
    """
    url = f"{BASE_URL}/fct_afs_wl.php"
    params = {
        "reg": reg or "",
        "tmfc1": tmfc1,
        "tmfc2": tmfc2,
        "tmef1": tmef1,
        "tmef2": tmef2,
        "disp": disp,
        "help": help,
        "authKey": KMA_API_KEY,
    }

    print(f"📡 [KMA] 중기 육상예보 요청 (reg={reg or 'ALL'})")
    return get_text(url, params, encoding="euc-kr")


def fetch_medium_marine_forecast(reg: str = "", disp: int = 0, help: int = 0,
                                tmfc1: str = "", tmfc2: str = "", tmef1: str = "", tmef2: str = ""):
    """
    중기 해상예보 조회
    reg   : 예보구역코드 (비워두면 전체)
    disp  : 출력형식 (0=기본, 1=구분자형)
    help  : 1이면 컬럼명 출력
    tmfc1~2 : 발표시각 범위 (YYYYMMDDHH, 생략 가능)
    tmef1~2 : 발효시각 범위 (YYYYMMDDHH, 생략 가능)
    
    ※ 중기예보는 단기와 달리 tmfc1~tmfc2, tmef1~tmef2를 지정하지 않아도 최신 데이터 반환.
    """
    url = f"{BASE_URL}/fct_afs_wo.php"
    params = {
        "reg": reg or "",
        "tmfc1": tmfc1,
        "tmfc2": tmfc2,
        "tmef1": tmef1,
        "tmef2": tmef2,
        "disp": disp,
        "help": help,
        "authKey": KMA_API_KEY,
    }

    print(f"📡 [KMA] 중기 해상예보 요청 (reg={reg or 'ALL'})")
    return get_text(url, params, encoding="euc-kr")

