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

// 해양 관측소 목록 조회
export const getMarineStations = async (limit = 100) => {
  const response = await api.get("/api/marine-stations", { params: { limit } });
  return response.data;
};

// 지상 관측소 목록 조회
export const getSurfaceStations = async (limit = 100) => {
  const response = await api.get("/api/surface-stations", { params: { limit } });
  return response.data;
};

// 스포츠 카테고리 목록 조회
export const getSports = async () => {
  const response = await api.get("/api/sports");
  return response.data;
};

// 지역 목록 조회
export const getRegions = async () => {
  const response = await api.get("/api/regions");
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

// 하위 호환성을 위해 유지되는 함수들 (사용되지 않을 수 있음)
export const getMarineSurface = async () => {
  console.warn("getMarineSurface is deprecated, use getMarineStations instead");
  return await getMarineStations();
};

export const getSurfaceObservations = async (params = {}) => {
  console.warn("getSurfaceObservations is deprecated, use getSurfaceStations instead");
  return await getSurfaceStations();
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
