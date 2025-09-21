import httpx
from typing import List, Dict, Any
from ...config import KMA_API_KEY
from .common import _to_float, KMAError, KMATimeoutError, KMAParsingError


def _parse_sea_obs_all(text: str) -> List[Dict[str, Any]]:
    """
    sea_obs.php 전체 지점 응답을 파싱하여 모든 지점 정보를 반환
    응답 형식: TP, TM, STN_ID, STN_KO, LON, LAT, WH, WD, WS, WS_GST, TW, TA, PA, HM, ...
    """
    try:
        lines = [ln for ln in text.splitlines() if ln.strip() and not ln.strip().startswith("#")]
        data_lines = [ln for ln in lines if "," in ln]

        stations = []
        for row in data_lines:
            cols = [c.strip() for c in row.split(",")]
            if len(cols) < 14:
                continue

            tp = cols[0]         # TP (관측종류)
            tm = cols[1]         # TM (관측시각)
            stn_id = cols[2]     # STN_ID
            stn_name = cols[3]   # STN_KO
            lon = _to_float(cols[4])  # LON (경도)
            lat = _to_float(cols[5])  # LAT (위도)
            wh = _to_float(cols[6])   # WH (유의파고)
            tw = _to_float(cols[10])  # TW (해수면 온도)

            # 위경도가 유효한 경우만 포함
            if lat is not None and lon is not None:
                station = {
                    "station_id": stn_id,
                    "station_name": stn_name,
                    "lat": lat,
                    "lon": lon,
                    "sst": tw,
                    "wave_height": wh,
                    "observed_at": tm,
                    "tp": tp,
                    "source": "KMA"
                }
                stations.append(station)

        return stations
    except Exception as e:
        raise KMAParsingError(f"Failed to parse sea observation data: {e}") from e


def _parse_marine_station_info(text: str) -> List[Dict[str, Any]]:
    """
    stn_inf.php BUOY 관측소 정보 응답을 파싱
    응답 형식: STNID, LON, LAT, STN_KO, FCT_ID, ...
    """
    try:
        lines = [ln for ln in text.splitlines() if ln.strip()]
        
        # 지상관측소와 같은 형식일 수 있으므로 #START7777 형식도 확인
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
            elif not line.startswith("#") and ("," in line or " " in line):
                # 마커가 없는 경우 데이터 라인으로 처리
                data_lines.append(line)

        stations = []
        for line in data_lines:
            # 쉼표로 구분된 경우와 공백으로 구분된 경우 모두 처리
            if "," in line:
                cols = [c.strip() for c in line.split(",")]
            else:
                cols = line.split()
            
            if len(cols) < 5:
                continue

            stnid = cols[0]      # STNID
            lon = _to_float(cols[1])    # LON (경도)
            lat = _to_float(cols[2])    # LAT (위도)
            stn_ko = cols[3]     # STN_KO (관측소명)
            fct_id = cols[4] if len(cols) > 4 else ""     # FCT_ID (예보구역 ID)

            # 위경도가 유효한 경우만 포함
            if lat is not None and lon is not None and stnid and stn_ko:
                station = {
                    "stnid": stnid,
                    "stn_ko": stn_ko,
                    "lat": lat,
                    "lon": lon,
                    "fct_id": fct_id,
                    "source": "KMA_BUOY"
                }
                stations.append(station)

        return stations
    except Exception as e:
        raise KMAParsingError(f"Failed to parse marine station info: {e}") from e


async def fetch_marine_station_info(client: httpx.AsyncClient, tm: str | None = None) -> List[Dict[str, Any]]:
    """해양 관측소 정보를 가져옴 (BUOY API)"""
    url = "https://apihub.kma.go.kr/api/typ01/url/stn_inf.php"
    params = {
        "inf": "BUOY",
        "stn": "",
        "authKey": KMA_API_KEY
    }
    if tm:
        params["tm"] = tm
    else:
        params["tm"] = "202211300900"  # 기본값

    try:
        r = await client.get(url, params=params, timeout=15)
        r.raise_for_status()
        
        stations = _parse_marine_station_info(r.text)
        print(f"✅ Fetched {len(stations)} marine station info")
        return stations
    except httpx.TimeoutException as e:
        raise KMATimeoutError(f"Timeout fetching marine station info: {e}") from e
    except httpx.HTTPStatusError as e:
        raise KMAError(f"HTTP error fetching marine station info: {e.response.status_code}") from e
    except KMAParsingError:
        raise  # Re-raise parsing errors as-is
    except Exception as e:
        raise KMAError(f"Unexpected error fetching marine station info: {type(e).__name__}: {e}") from e


async def fetch_all_marine_stations(client: httpx.AsyncClient, tm: str | None = None) -> List[Dict[str, Any]]:
    """모든 해양 관측소 데이터를 가져옴"""
    url = "https://apihub.kma.go.kr/api/typ01/url/sea_obs.php"
    params = {"stn": 0, "authKey": KMA_API_KEY}
    if tm:
        params["tm"] = tm

    try:
        r = await client.get(url, params=params, timeout=60)  # 타임아웃 60초로 증가
        r.raise_for_status()
        stations = _parse_sea_obs_all(r.text)
        return stations
    except httpx.TimeoutException as e:
        raise KMATimeoutError(f"Timeout fetching marine stations: {e}") from e
    except httpx.HTTPStatusError as e:
        raise KMAError(f"HTTP error fetching marine stations: {e.response.status_code}") from e
    except KMAParsingError:
        raise  # Re-raise parsing errors as-is
    except Exception as e:
        raise KMAError(f"Unexpected error fetching marine stations: {type(e).__name__}: {e}") from e