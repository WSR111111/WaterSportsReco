/**
 * 관측소 필터링 유틸리티
 * 관측값이 있는 관측소만 필터링하는 기능
 */

/**
 * 관측값이 있는 관측소 ID들을 추출
 * @param {Array} observations - 관측 데이터 배열
 * @returns {Set} 관측값이 있는 관측소 ID 집합
 */
export const getActiveStationIds = (observations) => {
  const activeIds = new Set();
  
  if (!Array.isArray(observations)) {
    return activeIds;
  }
  
  observations.forEach(stationData => {
    if (stationData?.station_id && 
        stationData?.observations && 
        Array.isArray(stationData.observations) && 
        stationData.observations.length > 0) {
      activeIds.add(stationData.station_id);
    }
  });
  
  return activeIds;
};

/**
 * 관측값이 있는 관측소만 필터링
 * @param {Array} stations - 관측소 목록
 * @param {Array} observations - 관측 데이터 배열
 * @returns {Object} 필터링된 관측소 정보
 */
export const filterActiveStations = (stations, observations) => {
  if (!Array.isArray(stations)) {
    return {
      activeStations: [],
      inactiveStations: [],
      totalStations: 0,
      activeCount: 0,
      inactiveCount: 0
    };
  }
  
  const activeStationIds = getActiveStationIds(observations);
  
  const activeStations = stations.filter(station => 
    activeStationIds.has(station.station_id)
  );
  
  const inactiveStations = stations.filter(station => 
    !activeStationIds.has(station.station_id)
  );
  
  return {
    activeStations,
    inactiveStations,
    totalStations: stations.length,
    activeCount: activeStations.length,
    inactiveCount: inactiveStations.length
  };
};

/**
 * 관측소 상태 정보 생성
 * @param {Array} surfaceStations - 지상 관측소 목록
 * @param {Array} surfaceObservations - 지상 관측 데이터
 * @param {Array} marineStations - 해양 관측소 목록  
 * @param {Array} marineObservations - 해양 관측 데이터
 * @returns {Object} 전체 관측소 상태 정보
 */
export const getStationsSummary = (surfaceStations, surfaceObservations, marineStations, marineObservations) => {
  const surfaceFilter = filterActiveStations(surfaceStations, surfaceObservations);
  const marineFilter = filterActiveStations(marineStations, marineObservations);
  
  const totalStations = surfaceFilter.totalStations + marineFilter.totalStations;
  const totalActive = surfaceFilter.activeCount + marineFilter.activeCount;
  const totalInactive = surfaceFilter.inactiveCount + marineFilter.inactiveCount;
  
  return {
    surface: surfaceFilter,
    marine: marineFilter,
    total: {
      totalStations,
      activeCount: totalActive,
      inactiveCount: totalInactive,
      activePercentage: totalStations > 0 ? Math.round((totalActive / totalStations) * 100) : 0
    }
  };
};

/**
 * 관측소가 활성 상태인지 확인
 * @param {string} stationId - 관측소 ID
 * @param {Array} observations - 관측 데이터 배열
 * @returns {boolean} 활성 상태 여부
 */
export const isStationActive = (stationId, observations) => {
  if (!Array.isArray(observations)) {
    return false;
  }
  
  return observations.some(stationData => 
    stationData?.station_id === stationId && 
    stationData?.observations && 
    Array.isArray(stationData.observations) && 
    stationData.observations.length > 0
  );
};

/**
 * 관측소 필터링 옵션
 */
export const STATION_FILTER_OPTIONS = {
  ACTIVE_ONLY: 'active_only',      // 활성 관측소만
  INACTIVE_ONLY: 'inactive_only',  // 비활성 관측소만
  ALL: 'all'                       // 모든 관측소
};

/**
 * 필터 옵션에 따라 관측소 목록 반환
 * @param {Array} stations - 관측소 목록
 * @param {Array} observations - 관측 데이터 배열
 * @param {string} filterOption - 필터 옵션
 * @returns {Array} 필터링된 관측소 목록
 */
export const getFilteredStations = (stations, observations, filterOption = STATION_FILTER_OPTIONS.ALL) => {
  const { activeStations, inactiveStations } = filterActiveStations(stations, observations);
  
  switch (filterOption) {
    case STATION_FILTER_OPTIONS.ACTIVE_ONLY:
      return activeStations;
    case STATION_FILTER_OPTIONS.INACTIVE_ONLY:
      return inactiveStations;
    case STATION_FILTER_OPTIONS.ALL:
    default:
      return stations;
  }
};