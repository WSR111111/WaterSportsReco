import { useEffect } from 'react';
import { calculateBounds } from '../utils/regionUtils';

export default function useMapNavigation(mapRef, geoData, selectedRegion, loaded) {
  
  // 지역 선택 시 지도 이동 
  const moveToRegion = (regionName) => {
    if (!mapRef.current || !window.kakao) return;

    // 전체 선택 시 한국 전체 보기
    if (!regionName || regionName === "전체") {
      const center = new window.kakao.maps.LatLng(35.9078, 127.7669);
      mapRef.current.setCenter(center);
      mapRef.current.setLevel(13);
      return;
    }

    // GeoJSON 데이터가 로드되지 않은 경우 대기
    if (!geoData || !geoData.features) {
      console.warn('⚠️ GeoJSON data not loaded yet');
      return;
    }

    // 지역명에서 특별시/광역시/도 제거하여 매칭
    const cleanRegionName = regionName
      .replace(/특별시|광역시|특별자치시|특별자치도|도$/g, '')
      .trim();

    // GeoJSON에서 해당 지역 찾기
    const feature = geoData.features.find(f => f.properties.name === cleanRegionName);

    if (feature) {
      const { center, bounds } = calculateBounds(feature.geometry.coordinates);
      const kakaoCenter = new window.kakao.maps.LatLng(center[1], center[0]);

      // 경계 크기에 따라 동적으로 줌 레벨 조정
      const latDiff = bounds.maxLat - bounds.minLat;
      const lngDiff = bounds.maxLng - bounds.minLng;
      const maxDiff = Math.max(latDiff, lngDiff);

      let level = 11;
      if (maxDiff > 2.5) level = 11;        // 매우 큰 지역 (강원도 등) - 더 넓게
      else if (maxDiff > 1.5) level = 11;   // 큰 지역 (경북, 경남 등) - 더 넓게
      else if (maxDiff > 0.8) level = 11;   // 중간 지역 (경기도 등) - 더 넓게
      else if (maxDiff > 0.4) level = 11;   // 작은 지역 (충남, 전북 등) - 더 넓게
      else if (maxDiff > 0.2) level = 11;    // 매우 작은 지역 (인천 등) - 더 넓게
      else level = 11;                       // 극소 지역 (서울, 부산 등) - 더 넓게

      mapRef.current.setCenter(kakaoCenter);
      mapRef.current.setLevel(level);
    }
  };

  // 지역 선택 시 지도 이동
  useEffect(() => {
    if (loaded && mapRef.current) {
      moveToRegion(selectedRegion);
    }
  }, [selectedRegion, loaded]);

  return { moveToRegion };
}