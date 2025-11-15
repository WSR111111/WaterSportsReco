"""
데이터 조회용 API 라우터
"""
from fastapi import APIRouter, Query
from typing import Optional, List
from app.database import get_db_manager

router = APIRouter(prefix="/data", tags=["Data Query"])

# 데이터베이스 매니저 인스턴스
db = get_db_manager()

@router.get("/leisure-places")
def get_leisure_places(
    region: Optional[str] = Query(None, description="지역 코드"),
    category: Optional[str] = Query(None, description="카테고리 코드"),
    limit: Optional[int] = Query(100, description="조회 개수 제한"),
    offset: Optional[int] = Query(0, description="조회 시작 위치")
):
    """레저 장소 목록 조회"""
    try:
        # 기본 쿼리
        query = """
        SELECT 
            lp.leisure_id,
            lp.content_id,
            lp.place_name,
            lp.address,
            lp.address2,
            lp.phone_number,
            lp.latitude,
            lp.longitude,
            lp.first_image,
            lp.first_image2,
            lp.cat_cd,
            cat.code_name as category_name,
            lp.reg_cd,
            reg.code_name as region_name
        FROM leisure_place lp
        LEFT JOIN code cat ON lp.cat_cd = cat.code
        LEFT JOIN code reg ON lp.reg_cd = reg.code
        WHERE 1=1
        """
        
        params = []
        
        # 지역 필터
        if region:
            query += " AND lp.reg_cd = %s"
            params.append(region)
            
        # 카테고리 필터
        if category:
            query += " AND lp.cat_cd = %s"
            params.append(category)
            
        # 정렬 및 페이징
        query += " ORDER BY lp.leisure_id LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        result = db.execute_query(query, params)
        
        return {
            "success": True,
            "data": result,
            "count": len(result)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "data": []
        }

@router.get("/leisure-place/{content_id}")
def get_leisure_place_detail(content_id: int):
    """특정 레저 장소 상세 정보 조회"""
    try:
        query = """
        SELECT 
            lp.leisure_id,
            lp.content_id,
            lp.place_name,
            lp.address,
            lp.address2,
            lp.phone_number,
            lp.latitude,
            lp.longitude,
            lp.first_image,
            lp.first_image2,
            lp.cat_cd,
            cat.code_name as category_name,
            lp.reg_cd,
            reg.code_name as region_name,
            lpd.homepage,
            lpd.overview
        FROM leisure_place lp
        LEFT JOIN code cat ON lp.cat_cd = cat.code
        LEFT JOIN code reg ON lp.reg_cd = reg.code
        LEFT JOIN leisure_place_detail lpd ON lp.content_id = lpd.content_id
        WHERE lp.content_id = %s
        """
        
        result = db.execute_query(query, [content_id])
        
        if result:
            return {
                "success": True,
                "data": result[0]
            }
        else:
            return {
                "success": False,
                "error": "장소를 찾을 수 없습니다",
                "data": None
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "data": None
        }

@router.get("/observation-stations")
def get_observation_stations(
    station_type: Optional[str] = Query(None, description="관측소 타입 (obs_ocean, obs_ground)"),
    limit: Optional[int] = Query(100, description="조회 개수 제한")
):
    """관측소 목록 조회"""
    try:
        query = """
        SELECT 
            os.station_id,
            os.station_nm,
            os.lat as latitude,
            os.lon as longitude,
            os.obs_cd,
            c.code_name as obs_name
        FROM observation_station os
        LEFT JOIN code c ON os.obs_cd = c.code
        WHERE 1=1
        """
        
        params = []
        
        if station_type:
            query += " AND os.obs_cd = %s"
            params.append(station_type)
            
        query += " ORDER BY os.station_id LIMIT %s"
        params.append(limit)
        
        result = db.execute_query(query, params)
        
        return {
            "success": True,
            "data": result,
            "count": len(result)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "data": []
        }

@router.get("/observation-data")
def get_observation_data(
    station_id: Optional[str] = Query(None, description="관측소 ID"),
    obs_cd: Optional[str] = Query(None, description="관측 코드"),
    limit: Optional[int] = Query(1000, description="조회 개수 제한")
):
    """관측 데이터 조회"""
    try:
        query = """
        SELECT 
            od.station_id,
            os.station_nm,
            od.obs_cd,
            c.code_name as obs_name,
            od.observation_value,
            od.observed_at
        FROM observation_data od
        LEFT JOIN observation_station os ON od.station_id = os.station_id
        LEFT JOIN code c ON od.obs_cd = c.code
        WHERE 1=1
        """
        
        params = []
        
        if station_id:
            query += " AND od.station_id = %s"
            params.append(station_id)
            
        if obs_cd:
            # obs_cd가 패턴인 경우 (예: obs_ocean, obs_ground) LIKE 검색 사용
            if obs_cd in ['obs_ocean', 'obs_ground']:
                query += " AND od.obs_cd LIKE %s"
                params.append(f"{obs_cd}_%")
            else:
                query += " AND od.obs_cd = %s"
                params.append(obs_cd)
            
        query += " ORDER BY od.observed_at DESC LIMIT %s"
        params.append(limit)
        
        result = db.execute_query(query, params)
        
        # 관측소별, 관측항목별로 최신 데이터만 그룹화
        stations_data = {}
        for row in result:
            station_id = row['station_id']
            obs_cd = row['obs_cd']
            
            if station_id not in stations_data:
                stations_data[station_id] = {
                    'station_id': station_id,
                    'station_nm': row['station_nm'],
                    'observations': {},  # dict로 변경하여 obs_cd별로 최신 데이터만 저장
                    'latest_observations': []
                }
            
            # 각 관측 항목별로 최신 데이터만 유지
            current_obs = {
                'obs_cd': obs_cd,
                'obs_name': row['obs_name'],
                'observation_value': row['observation_value'],
                'observed_at': row['observed_at']
            }
            
            # 이미 해당 관측 항목이 있다면 시간 비교
            if obs_cd in stations_data[station_id]['observations']:
                existing_time = stations_data[station_id]['observations'][obs_cd]['observed_at']
                current_time = row['observed_at']
                
                # 현재 데이터가 더 최신이면 교체
                if current_time > existing_time:
                    stations_data[station_id]['observations'][obs_cd] = current_obs
            else:
                # 처음 나오는 관측 항목이면 추가
                stations_data[station_id]['observations'][obs_cd] = current_obs
        
        # dict를 list로 변환
        for station_id in stations_data:
            stations_data[station_id]['observations'] = list(stations_data[station_id]['observations'].values())
            del stations_data[station_id]['latest_observations']  # 불필요한 키 제거
        
        grouped_data = list(stations_data.values())
        
        return {
            "success": True,
            "data": grouped_data,
            "count": len(grouped_data)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "data": []
        }

@router.get("/regions")
def get_regions():
    """지역 목록 조회"""
    try:
        query = """
        SELECT code, code_name, code_desc
        FROM code 
        WHERE upper_code = 'reg' AND code != 'reg'
        ORDER BY code
        """
        
        result = db.execute_query(query)
        
        return {
            "success": True,
            "data": result,
            "count": len(result)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "data": []
        }

@router.get("/categories")
def get_categories():
    """스포츠 카테고리 목록 조회"""
    try:
        query = """
        SELECT code, code_name, code_desc
        FROM code 
        WHERE upper_code = 'cat' AND code != 'cat'
        ORDER BY code
        """
        
        result = db.execute_query(query)
        
        return {
            "success": True,
            "data": result,
            "count": len(result)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "data": []
        }