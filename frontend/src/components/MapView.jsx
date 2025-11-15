import { useEffect, useRef, useState } from "react";
import useKakaoLoader from "../hooks/useKakaoLoader";
import useMapNavigation from "../hooks/useMapNavigation";
import { useLeisurePlaces, useObservationStations, useObservationDataByType } from "../hooks/useData";
import ActivityFilter from "./ActivityFilter";
import PlaceMarkers from "./PlaceMarkers";
import ObservationStationMarkers from "./ObservationStationMarkers";


const KAKAO_APPKEY = import.meta.env.VITE_KAKAO_API_KEY;

export default function MapView({ selectedRegion, onRegionSelect }) {
  const { loaded, error } = useKakaoLoader(KAKAO_APPKEY);
  const mapRef = useRef(null);
  const containerRef = useRef(null);
  const infoWindowRef = useRef(null);
  const touristMarkersRef = useRef([]);
  const observationMarkersRef = useRef([]);

  // 실제 DB 데이터 사용 - 지역 필터링은 프론트엔드에서 처리
  const { places, loading: placesLoading } = useLeisurePlaces({
    limit: 1000  // 모든 데이터를 가져와서 프론트엔드에서 필터링
  });

  const { stations: marineStations, loading: marineLoading } = useObservationStations('obs_ocean');
  const { stations: surfaceStations, loading: surfaceLoading } = useObservationStations('obs_ground');
  const { observations: marineObservations, loading: marineObsLoading, error: marineObsError } = useObservationDataByType('marine');
  const { observations: surfaceObservations, loading: surfaceObsLoading, error: surfaceObsError } = useObservationDataByType('surface');

  // 관측 데이터 에러 로깅
  useEffect(() => {
    if (marineObsError) {
      console.error('🌊 해양 관측 데이터 에러:', marineObsError);
    }
    if (surfaceObsError) {
      console.error('🏢 지상 관측 데이터 에러:', surfaceObsError);
    }
  }, [marineObsError, surfaceObsError]);

  const [selectedWaterSport, setSelectedWaterSport] = useState(null);
  const loading = placesLoading || marineLoading || surfaceLoading || marineObsLoading || surfaceObsLoading;

  const [showObservationStations, setShowObservationStations] = useState(false);
  
  // showObservationStations 상태 변경 로그
  useEffect(() => {
    console.log('🔄 MapView - showObservationStations 상태 변경:', showObservationStations);
  }, [showObservationStations]);
  const [geoData, setGeoData] = useState(null);


  // GeoJSON 데이터 로드
  useEffect(() => {
    fetch('/geo/korea_sido_simple.json')
      .then(response => response.json())
      .then(data => {
        setGeoData(data);

      })
      .catch(error => {
        console.error('❌ Failed to load GeoJSON:', error);
      });
  }, []);

  // 지도 네비게이션 훅 사용
  useMapNavigation(mapRef, geoData, selectedRegion, loaded);

  // 기존 fetchAllData 함수 제거 - 이제 useData 훅을 사용





  // 지도 초기화
  useEffect(() => {
    if (!loaded || !containerRef.current) return;

    try {
      const { kakao } = window;
      if (!kakao?.maps) return;

      const center = new kakao.maps.LatLng(35.9078, 127.7669);
      const map = new kakao.maps.Map(containerRef.current, { center, level: 13 });
      mapRef.current = map;

      setTimeout(() => {
        map.relayout();
        map.setCenter(center);
      }, 100);
    } catch (error) {
      console.error("❌ Map initialization failed:", error);
    }
  }, [loaded]);

  // 기존 데이터 로드 useEffect 제거 - 이제 useData 훅이 자동으로 처리



  // 에러 및 로딩 상태 처리
  if (!KAKAO_APPKEY) {
    return (
      <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "100%", flexDirection: "column", backgroundColor: "#f5f5f5" }}>
        <h3>카카오맵 API 키가 설정되지 않았습니다</h3>
        <p>.env 파일에 VITE_KAKAO_API_KEY를 설정해주세요</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "100%", flexDirection: "column", backgroundColor: "#f5f5f5" }}>
        <h3>지도 로딩 오류</h3>
        <p>{error.message}</p>
        <button onClick={() => window.location.reload()} style={{ padding: "8px 16px", backgroundColor: "#007bff", color: "white", border: "none", borderRadius: "4px", cursor: "pointer" }}>
          새로고침
        </button>
      </div>
    );
  }

  if (!loaded) {
    return (
      <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "100%", backgroundColor: "#f5f5f5", color: "#666" }}>
        <div>지도 로딩 중...</div>
      </div>
    );
  }

  return (
    <div style={{ position: "relative", width: "100%", height: "100%" }}>
      <div ref={containerRef} style={{ width: "100%", height: "100%" }} />

      {/* 활동 필터 */}
      <ActivityFilter
        selectedRegion={selectedRegion}
        selectedWaterSport={selectedWaterSport}
        onRegionSelect={onRegionSelect}
        onWaterSportSelect={setSelectedWaterSport}
        showObservationStations={showObservationStations}
        onObservationStationsToggle={setShowObservationStations}
      />

      {/* 마커 컴포넌트들 */}
      <PlaceMarkers
        places={places}
        selectedRegion={selectedRegion}
        selectedWaterSport={selectedWaterSport}
        mapRef={mapRef}
        touristMarkersRef={touristMarkersRef}
        infoWindowRef={infoWindowRef}
      />

      <ObservationStationMarkers
        marineStations={marineStations}
        surfaceStations={surfaceStations}
        marineObservations={marineObservations}
        surfaceObservations={surfaceObservations}
        showObservationStations={showObservationStations}
        mapRef={mapRef}
        observationMarkersRef={observationMarkersRef}
        infoWindowRef={infoWindowRef}
      />




    </div>
  );
}