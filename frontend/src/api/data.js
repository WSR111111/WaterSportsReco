/**
 * 실제 DB 데이터 조회 API 클라이언트
 */
import client from './client.js';

// 레저 장소 목록 조회
export const getLeisurePlaces = async (params = {}) => {
  try {
    const response = await client.get('/api/data/leisure-places', { params });
    return response.data;
  } catch (error) {
    console.error('레저 장소 조회 실패:', error);
    throw error;
  }
};

// 관측소 목록 조회
export const getObservationStations = async (params = {}) => {
  try {
    const response = await client.get('/api/data/observation-stations', { params });
    return response.data;
  } catch (error) {
    console.error('관측소 조회 실패:', error);
    throw error;
  }
};

// 관측 데이터 조회
export const getObservationData = async (params = {}) => {
  try {
    const response = await client.get('/api/data/observation-data', { params });
    return response.data;
  } catch (error) {
    console.error('관측 데이터 조회 실패:', error);
    throw error;
  }
};

// 지역 목록 조회
export const getRegions = async () => {
  try {
    const response = await client.get('/api/data/regions');
    return response.data;
  } catch (error) {
    console.error('지역 목록 조회 실패:', error);
    throw error;
  }
};

// 스포츠 카테고리 목록 조회
export const getCategories = async () => {
  try {
    const response = await client.get('/api/data/categories');
    return response.data;
  } catch (error) {
    console.error('카테고리 조회 실패:', error);
    throw error;
  }
};