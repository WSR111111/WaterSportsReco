/**
 * 실제 DB 데이터를 사용하는 커스텀 훅들
 */
import { useState, useEffect } from 'react';
import { 
  getLeisurePlaces, 
  getObservationStations, 
  getObservationData,
  getRegions,
  getCategories 
} from '../api/data.js';

// 레저 장소 데이터 훅
export const useLeisurePlaces = (filters = {}) => {
  const [places, setPlaces] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchPlaces = async () => {
      try {
        setLoading(true);
        const response = await getLeisurePlaces(filters);
        setPlaces(response.data || []);
        setError(null);
      } catch (err) {
        setError(err.message);
        setPlaces([]);
      } finally {
        setLoading(false);
      }
    };

    fetchPlaces();
  }, [JSON.stringify(filters)]);

  return { places, loading, error, refetch: () => fetchPlaces() };
};

// 관측소 데이터 훅
export const useObservationStations = (stationType = null) => {
  const [stations, setStations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStations = async () => {
      try {
        setLoading(true);
        const params = stationType ? { station_type: stationType } : {};
        const response = await getObservationStations(params);
        setStations(response.data || []);
        setError(null);
      } catch (err) {
        setError(err.message);
        setStations([]);
      } finally {
        setLoading(false);
      }
    };

    fetchStations();
  }, [stationType]);

  return { stations, loading, error };
};

// 관측 데이터 훅
export const useObservationData = (stationId = null, obsCode = null) => {
  const [observations, setObservations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchObservations = async () => {
      try {
        setLoading(true);
        const params = {};
        if (stationId) params.station_id = stationId;
        if (obsCode) params.obs_cd = obsCode;
        
        const response = await getObservationData(params);
        
        // 백엔드에서 관측소별로 그룹화된 데이터를 받음
        // 각 항목은 { station_id, station_nm, observations: [...] } 구조
        const processedData = (response.data || []).map(stationData => {
          // observations 배열을 평면화하여 각 관측값을 개별 객체로 변환
          const flattenedObservations = (stationData.observations || []).map(obs => ({
            station_id: stationData.station_id,
            station_nm: stationData.station_nm,
            obs_cd: obs.obs_cd,
            obs_name: obs.obs_name,
            observation_value: obs.observation_value,
            observed_at: obs.observed_at
          }));
          
          return flattenedObservations;
        }).flat(); // 중첩 배열을 평면화
        
        setObservations(processedData);
        setError(null);
      } catch (err) {
        console.error('관측 데이터 조회 실패:', err);
        setError(err.message);
        setObservations([]);
      } finally {
        setLoading(false);
      }
    };

    fetchObservations();
  }, [stationId, obsCode]);

  return { observations, loading, error };
};

// 관측소 타입별 관측 데이터 훅
export const useObservationDataByType = (stationType) => {
  const [observations, setObservations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchObservations = async () => {
      try {
        setLoading(true);
        setError(null);
        
        console.log(`🔍 ${stationType} 관측 데이터 조회 시작`);
        
        // 관측소 타입에 따라 관측 항목 코드 결정
        let obsCodePattern = null;
        if (stationType === 'marine') {
          obsCodePattern = 'obs_ocean';
        } else if (stationType === 'surface') {
          obsCodePattern = 'obs_ground';
        }
        
        if (!obsCodePattern) {
          console.warn(`❌ 알 수 없는 관측소 타입: ${stationType}`);
          setObservations([]);
          return;
        }
        
        console.log(`📡 API 호출: obs_cd=${obsCodePattern}`);
        const params = { obs_cd: obsCodePattern, limit: 1000 }; // limit을 1000으로 증가
        const response = await getObservationData(params);
        
        console.log(`📥 API 응답:`, response);
        
        // 응답 데이터 검증
        if (!response || !response.data) {
          console.warn(`⚠️ ${stationType} 관측 데이터 응답이 비어있습니다:`, response);
          setObservations([]);
          return;
        }
        
        // 백엔드에서 관측소별로 그룹화된 데이터를 받음
        const processedData = response.data.map(stationData => {
          if (!stationData || typeof stationData !== 'object') {
            console.warn('❌ 잘못된 관측소 데이터 형식:', stationData);
            return [];
          }
          
          console.log(`📊 관측소 ${stationData.station_id} (${stationData.station_nm}): ${(stationData.observations || []).length}개 관측값`);
          
          // observations 배열을 평면화하여 각 관측값을 개별 객체로 변환
          return (stationData.observations || []).map(obs => ({
            station_id: stationData.station_id,
            station_nm: stationData.station_nm,
            obs_cd: obs.obs_cd,
            obs_name: obs.obs_name,
            observation_value: obs.observation_value,
            observed_at: obs.observed_at
          }));
        }).flat(); // 중첩 배열을 평면화
        
        setObservations(processedData);
        console.log(`✅ ${stationType} 관측 데이터 로드 완료: ${processedData.length}개 관측소`);
        
        // 데이터가 없는 경우 추가 디버깅 정보
        if (processedData.length === 0) {
          console.warn(`⚠️ ${stationType} 관측 데이터가 없습니다. 데이터베이스를 확인해주세요.`);
        }
        
      } catch (err) {
        console.error(`❌ ${stationType} 관측 데이터 조회 실패:`, err);
        const errorMessage = err.response?.data?.detail || err.message || '관측 데이터를 불러올 수 없습니다';
        setError(errorMessage);
        setObservations([]);
      } finally {
        setLoading(false);
      }
    };

    if (stationType) {
      fetchObservations();
    } else {
      setLoading(false);
      setObservations([]);
    }
  }, [stationType]);

  return { observations, loading, error };
};

// 지역 목록 훅
export const useRegions = () => {
  const [regions, setRegions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchRegions = async () => {
      try {
        setLoading(true);
        const response = await getRegions();
        setRegions(response.data || []);
        setError(null);
      } catch (err) {
        setError(err.message);
        setRegions([]);
      } finally {
        setLoading(false);
      }
    };

    fetchRegions();
  }, []);

  return { regions, loading, error };
};

// 카테고리 목록 훅
export const useCategories = () => {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        setLoading(true);
        const response = await getCategories();
        setCategories(response.data || []);
        setError(null);
      } catch (err) {
        setError(err.message);
        setCategories([]);
      } finally {
        setLoading(false);
      }
    };

    fetchCategories();
  }, []);

  return { categories, loading, error };
};