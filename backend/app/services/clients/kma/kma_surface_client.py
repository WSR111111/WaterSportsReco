import httpx
from typing import List, Dict, Any
from ....config import KMA_API_KEY
from .common import _to_float


def _parse_surface_obs(text: str) -> List[Dict[str, Any]]:
    
    lines = [ln for ln in text.splitlines() if ln.strip()]
    
    data_lines = []
    in_data_section = False
    
    for line in lines:
        if line.startswith("#START7777"):
            in_data_section = True
            continue
        elif line.startswith("#7777END"):
            break
        elif in_data_section and not line.startswith("#"):
            data_lines.append(line)
    
    stations = []
    for line in data_lines:
        parts = line.split()
        if len(parts) < 15:  # 최소 필요한 필드 수
            continue
        
        try:
            datetime_str = parts[0]  # YYMMDDHHMI
            station_id = parts[1]    # STN
            wind_dir = _to_float(parts[2])      # WD (풍향)
            wind_speed = _to_float(parts[3])    # WS (풍속)
            gust_speed = _to_float(parts[4])    # GST (돌풍)
            pressure = _to_float(parts[7])      # PA (기압)
            temp = _to_float(parts[11])         # TA (기온)
            humidity = _to_float(parts[13])     # HM (습도)
            
            # WH 파고는 뒤에서 4번째 위치 (BF IR IX 앞)
            if len(parts) >= 4:
                wh_index = len(parts) - 4  # 뒤에서 4번째
                wave_height = _to_float(parts[wh_index])
            
            station = {
                "station_id": station_id,
                "datetime": datetime_str,
                "wind_direction": wind_dir,
                "wind_speed": wind_speed,
                "gust_speed": gust_speed,
                "pressure": pressure,
                "temperature": temp,
                "humidity": humidity,
                "wave_height": wave_height, 
                "source": "KMA_SURFACE"
            }
            stations.append(station)
            
        except (IndexError, ValueError) as e:
            print(f"❌ Error parsing line: {e}")
            continue
    
    print(f"✅ Parsed {len(stations)} surface observations")
    return stations


async def fetch_surface_obs(
    client: httpx.AsyncClient, 
    tm1: str | None = None,
    tm2: str | None = None, 
    stn: str | None = None
) -> List[Dict[str, Any]]:
    """
    KMA 지상 관측 데이터를 가져옴
    API: https://apihub.kma.go.kr/api/typ01/url/kma_sfctm2.php
    """
    url = "https://apihub.kma.go.kr/api/typ01/url/kma_sfctm2.php"
    params = {"authKey": KMA_API_KEY}
    
    if tm1:
        params["tm"] = tm1
    else:
        params["tm"] = ""
        
    if stn:
        params["stn"] = stn
    else:
        params["stn"] = ""
    
    params["help"] = ""
    
    try:
        print(f"🔍 Fetching surface observations from: {url}")
        print(f"🔍 Parameters: {params}")
        
        r = await client.get(url, params=params, timeout=60)
        r.raise_for_status()
        
        print(f"📡 Response status: {r.status_code}")
        print(f"📡 Response length: {len(r.text)} characters")
        
        stations = _parse_surface_obs(r.text)
        return stations
    except Exception as e:
        print(f"❌ Error fetching surface observations: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return []


def _parse_station_info(text: str) -> List[Dict[str, Any]]:
    """
    stn_inf.php 관측소 정보 응답을 파싱하여 관측소 정보를 반환
    """
    lines = [ln for ln in text.splitlines() if ln.strip()]
    
    data_lines = []
    in_data_section = False
    
    for line in lines:
        if line.startswith("#START7777"):
            in_data_section = True
            continue
        elif line.startswith("#7777END"):
            break
        elif in_data_section and not line.startswith("#"):
            data_lines.append(line)
    
    stations = []
    for line in data_lines:
        parts = line.split()
        if len(parts) < 13:
            continue
        
        try:
            station_id = parts[0]        # STN_ID
            lon = _to_float(parts[1])    # LON (경도)
            lat = _to_float(parts[2])    # LAT (위도)
            station_code = parts[9]      # STN_CD
            station_name_ko = parts[10]  # STN_KO (한글명)
            station_name_en = parts[11]  # STN_EN (영문명)
            fct_id = parts[12] if len(parts) > 12 else ""  # FCT_ID (예보구역 ID)
            
            if lat is not None and lon is not None and station_id and station_name_ko:
                station = {
                    "stnid": station_id,
                    "stn_ko": station_name_ko,
                    "station_name_en": station_name_en,
                    "station_code": station_code,
                    "lat": lat,
                    "lon": lon,
                    "fct_id": fct_id,
                    "source": "KMA_SFC"
                }
                stations.append(station)
                
        except (IndexError, ValueError):
            continue
    
    return stations


async def fetch_surface_station_info(
    client: httpx.AsyncClient,
    tm: str | None = None
) -> List[Dict[str, Any]]:
    """
    KMA 지상 관측소 정보를 가져옴
    API: https://apihub.kma.go.kr/api/typ01/url/stn_inf.php
    """
    url = "https://apihub.kma.go.kr/api/typ01/url/stn_inf.php"
    params = {
        "inf": "SFC", 
        "stn": "",    
        "help": "1",
        "authKey": KMA_API_KEY
    }
    
    if tm:
        params["tm"] = tm
    else:
        from datetime import datetime, timedelta
        default_time = datetime.now() - timedelta(hours=1)
        params["tm"] = default_time.strftime("%Y%m%d%H00")
    
    try:
        print(f"🔍 Fetching surface station info from: {url}")
        print(f"🔍 Parameters: {params}")
        
        r = await client.get(url, params=params, timeout=60)
        r.raise_for_status()
        
        print(f"📡 Response status: {r.status_code}")
        print(f"📡 Response length: {len(r.text)} characters")
        
        stations = _parse_station_info(r.text)
        print(f"✅ Parsed {len(stations)} surface station info")
        return stations
        
    except Exception as e:
        print(f"❌ Error fetching surface station info: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return []