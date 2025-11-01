import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_BACKEND_URL || "http://localhost:8000",
});

// 실제 DB에서 데이터를 조회하는 API들 (현재 백엔드 구조에 맞게 수정)

// 레저 장소 목록 조회
export const getPlaces = async (params = {}) => {
  const response = await api.get("/api/data/leisure-places", { params });
  return { places: response.data.data || [] };
};

// 지도용 레저 장소 목록 조회 (좌표 있는 것만)
export const getMapPlaces = async (params = {}) => {
  const response = await api.get("/api/data/leisure-places", { params });
  // 좌표가 있는 것만 필터링
  const placesWithCoords = (response.data.data || []).filter(place => 
    place.latitude && place.longitude
  );
  return { places: placesWithCoords };
};

// 해양 관측 데이터 조회
export const getMarineObservations = async (params = {}) => {
  const response = await api.get("/api/data/observation-data", { 
    params: { obs_cd: 'obs_ocean_TW', ...params } 
  });
  // 관측소별로 그룹화하여 stations 형태로 반환
  const stations = {};
  (response.data.data || []).forEach(obs => {
    if (!stations[obs.station_id]) {
      stations[obs.station_id] = {
        station_id: obs.station_id,
        station_nm: obs.station_nm,
        observations: []
      };
    }
    stations[obs.station_id].observations.push({
      obs_cd: obs.obs_cd,
      observation_value: obs.observation_value,
      observed_at: obs.observed_at,
      obs_name: obs.obs_name
    });
  });
  return { stations: Object.values(stations) };
};

// 지상 관측 데이터 조회
export const getSurfaceObservations = async (params = {}) => {
  const response = await api.get("/api/data/observation-data", { 
    params: { obs_cd: 'obs_ground_TA', ...params } 
  });
  // 관측소별로 그룹화하여 stations 형태로 반환
  const stations = {};
  (response.data.data || []).forEach(obs => {
    if (!stations[obs.station_id]) {
      stations[obs.station_id] = {
        station_id: obs.station_id,
        station_nm: obs.station_nm,
        observations: []
      };
    }
    stations[obs.station_id].observations.push({
      obs_cd: obs.obs_cd,
      observation_value: obs.observation_value,
      observed_at: obs.observed_at,
      obs_name: obs.obs_name
    });
  });
  return { stations: Object.values(stations) };
};

// 관측소 목록 조회
export const getObservationStations = async (params = {}) => {
  let station_type = null;
  if (params.category === "MARINE") {
    station_type = "obs_ocean";
  } else if (params.category === "SURFACE") {
    station_type = "obs_ground";
  }
  
  const response = await api.get("/api/data/observation-stations", { 
    params: { station_type, ...params } 
  });
  return { stations: response.data.data || [] };
};

// 해양 관측소 목록 조회 (하위 호환성)
export const getMarineStations = async () => {
  const response = await api.get("/api/data/observation-stations", { 
    params: { station_type: "obs_ocean" } 
  });
  return { stations: response.data.data || [] };
};

// 지상 관측소 목록 조회 (하위 호환성)
export const getSurfaceStations = async () => {
  const response = await api.get("/api/data/observation-stations", { 
    params: { station_type: "obs_ground" } 
  });
  return { stations: response.data.data || [] };
};

// 스포츠 카테고리 목록 조회
export const getSports = async () => {
  const response = await api.get("/api/data/categories");
  return { categories: response.data.data || [] };
};

// 지역 목록 조회
export const getRegions = async () => {
  const response = await api.get("/api/data/regions");
  return { regions: response.data.data || [] };
};

// 지역 데이터 동기화
export const syncRegions = async () => {
  const response = await api.post("/api/region/sync");
  return response.data;
};

// 특정 장소의 상세 정보 조회
export const getPlaceDetail = async (contentId) => {
  const response = await api.get(`/api/data/leisure-place/${contentId}`);
  return response.data.data; // 새로운 응답 구조에 맞게 수정
};

// 기존 API와의 호환성을 위한 래퍼 함수들
export const getTouristSpots = async (params = {}) => {
  // 파라미터 매핑: 기존 파라미터를 새 API에 맞게 변환
  const mappedParams = {};
  if (params.cat3) {
    // cat3는 카테고리 코드로 사용 (현재는 지원하지 않으므로 무시)
  }
  if (params.area_code) {
    mappedParams.region = params.area_code;
  }
  if (params.sigungu_code) {
    // sigungu_code는 현재 지원하지 않으므로 무시
  }
  
  const response = await api.get("/api/data/leisure-places", { params: mappedParams });
  return { tourist_spots: response.data.data || [] };
};

export const getMarineSurface = async () => {
  console.warn("getMarineSurface is deprecated, use getMarineStations instead");
  return await getMarineStations();
};

export const getSurfaceObservationsDeprecated = async (params = {}) => {
  console.warn("getSurfaceObservationsDeprecated is deprecated, use getSurfaceObservations instead");
  return await getSurfaceObservations(params);
};

export const getPlacesInRect = async (rect, activities) => {
  console.warn("getPlacesInRect is deprecated, use getPlaces instead");
  return await getPlaces({ activities });
};

export const getTouristSpotDetail = async (contentId) => {
  console.warn("getTouristSpotDetail is deprecated, use getPlaces with content_id filter instead");
  // content_id로 특정 장소 조회 (현재 API에서는 지원하지 않으므로 전체 조회 후 필터링)
  const response = await api.get("/api/data/leisure-places", { params: { limit: 1000 } });
  const places = response.data.data || [];
  const place = places.find(p => p.content_id == contentId);
  return place ? { places: [place] } : { places: [] };
};

export default api;
