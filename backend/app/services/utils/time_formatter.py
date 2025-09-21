from datetime import datetime, timedelta
from typing import Optional


def format_kma_datetime(datetime_str: str) -> Optional[str]:
    """KMA API 시간 형식을 MySQL DATETIME 형식으로 변환"""
    if not datetime_str:
        return None
    
    try:
        if len(datetime_str) == 10:  # YYMMDDHHMI 형식
            # 20을 앞에 붙여서 4자리 연도로 변환
            return f"20{datetime_str[:2]}-{datetime_str[2:4]}-{datetime_str[4:6]} {datetime_str[6:8]}:{datetime_str[8:10]}:00"
        elif len(datetime_str) >= 12:  # YYYYMMDDHHMM 형식
            return f"{datetime_str[:4]}-{datetime_str[4:6]}-{datetime_str[6:8]} {datetime_str[8:10]}:{datetime_str[10:12]}:00"
        else:
            return None
    except Exception:
        return None


def get_current_kma_time() -> str:
    """현재 시간을 KMA API 형식(YYYYMMDDHHMM)으로 반환"""
    return datetime.now().strftime("%Y%m%d%H%M")


def get_previous_hour_kma_time() -> str:
    """1시간 전 시간을 KMA API 형식(YYYYMMDDHHMM)으로 반환"""
    previous_hour = datetime.now() - timedelta(hours=1)
    return previous_hour.strftime("%Y%m%d%H00")  # 분은 00으로 설정


def validate_kma_time_format(time_str: str) -> bool:
    """KMA API 시간 형식이 유효한지 검증"""
    if not time_str:
        return False
    
    if len(time_str) == 10:  # YYMMDDHHMI
        try:
            datetime.strptime(f"20{time_str}", "%Y%m%d%H%M")
            return True
        except ValueError:
            return False
    elif len(time_str) == 12:  # YYYYMMDDHHMM
        try:
            datetime.strptime(time_str, "%Y%m%d%H%M")
            return True
        except ValueError:
            return False
    
    return False