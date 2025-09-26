import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_BACKEND_URL || "http://localhost:8000",
});

// DB에서 데이터를 조회하는 새로운 API들

// 레저 장소 목록 조회
export const getPlaces = async (params = {}) => {
  const response = await api.get("/api/places", { params });
  return response.data;
};

// 지도용 레저 장소 목록 조회 (좌표 있는 것만)
export const getMapPlaces = async (params = {}) => {
  const response = await api.get("/api/leisure/map/places", { params });
  return response.data;
};

// 해양 관측 데이터 조회
export const getMarineObservations = async (params = {}) => {
  const response = await api.get("/api/observation/marine", { params });
  return response.data;
};

// 지상 관측 데이터 조회
export const getSurfaceObservations = async (params = {}) => {
  const response = await api.get("/api/observation/surface", { params });
  return response.data;
};

// 관측소 목록 조회
export const getObservationStations = async (params = {}) => {
  const response = await api.get("/api/observation/stations", { params });
  return response.data;
};

// 해양 관측소 목록 조회 (하위 호환성)
export const getMarineStations = async () => {
  const response = await api.get("/api/observation/stations", { params: { category: "MARINE" } });
  return response.data;
};

// 지상 관측소 목록 조회 (하위 호환성)
export const getSurfaceStations = async () => {
  const response = await api.get("/api/observation/stations", { params: { category: "SURFACE" } });
  return response.data;
};

// 스포츠 카테고리 목록 조회
export const getSports = async () => {
  const response = await api.get("/api/sports/list");
  return response.data;
};

// 지역 목록 조회
export const getRegions = async () => {
  const response = await api.get("/api/region/list");
  return response.data;
};

// 지역 데이터 동기화
export const syncRegions = async () => {
  const response = await api.post("/api/region/sync");
  return response.data;
};

// 특정 장소의 상세 정보 조회
export const getPlaceDetail = async (contentId) => {
  const response = await api.get(`/api/leisure/place/${contentId}`);
  return response.data;
};

// 기존 API와의 호환성을 위한 래퍼 함수들
export const getTouristSpots = async (params = {}) => {
  // cat3 파라미터를 cat3로 매핑
  const mappedParams = {};
  if (params.cat3) {
    mappedParams.cat3 = params.cat3;
  }
  if (params.area_code) {
    mappedParams.area_code = params.area_code;
  }
  if (params.sigungu_code) {
    mappedParams.sigungu_code = params.sigungu_code;
  }
  
  const response = await api.get("/api/places", { params: mappedParams });
  return { tourist_spots: response.data.places };
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
  return await getPlaces({ content_id: contentId });
};

export default api;
