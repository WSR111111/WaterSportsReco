"""KMA API 공통 유틸리티 함수들"""


def _to_float(token: str) -> float | None:
    """문자열을 float로 변환, 실패시 None 반환"""
    try:
        cleaned = token.strip()
        if not cleaned or cleaned == "-":
            return None
        
        value = float(cleaned)
        return value
    except Exception:
        return None


class KMAError(Exception):
    """KMA API 관련 기본 예외"""
    pass


class KMATimeoutError(KMAError):
    """KMA API 타임아웃 예외"""
    pass


class KMAParsingError(KMAError):
    """KMA API 응답 파싱 예외"""
    pass