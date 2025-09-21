import json
from typing import Dict, Any, List


def parse_json_response(response_text: str) -> Dict[str, Any]:
    """JSON 응답을 파싱하여 기본 구조를 반환"""
    try:
        data = json.loads(response_text)
        
        response = data.get('response', {})
        header = response.get('header', {})
        
        # 응답 상태 확인
        result_code = header.get('resultCode', '')
        if result_code != '0000':
            result_msg = header.get('resultMsg', 'Unknown error')
            return {
                'success': False,
                'error_code': result_code,
                'error_message': result_msg,
                'data': []
            }
        
        # 데이터 추출
        body = response.get('body', {})
        items = body.get('items', {})
        
        # item이 리스트인지 단일 객체인지 확인
        item_data = items.get('item', [])
        if isinstance(item_data, dict):
            item_data = [item_data]
        elif not isinstance(item_data, list):
            item_data = []
        
        return {
            'success': True,
            'data': item_data,
            'total_count': body.get('totalCount', len(item_data))
        }
        
    except json.JSONDecodeError as e:
        return {
            'success': False,
            'error_code': 'JSON_PARSE_ERROR',
            'error_message': str(e),
            'data': []
        }
    except Exception as e:
        return {
            'success': False,
            'error_code': 'UNKNOWN_ERROR',
            'error_message': str(e),
            'data': []
        }


def safe_float_convert(value: str) -> float | None:
    """문자열을 안전하게 float로 변환"""
    if not value or value.strip() == '':
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def safe_int_convert(value: str) -> int | None:
    """문자열을 안전하게 int로 변환"""
    if not value or value.strip() == '':
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None