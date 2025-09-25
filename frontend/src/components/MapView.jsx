import { useEffect, useRef, useState } from "react";
import useKakaoLoader from "../hooks/useKakaoLoader";
import useMapNavigation from "../hooks/useMapNavigation";
import { getMapPlaces, getObservationStations, getMarineObservations, getSurfaceObservations } from "../api/client";
import ActivityFilter from "./ActivityFilter";
import PlaceMarkers from "./PlaceMarkers";
import MarineStationMarkers from "./MarineStationMarkers";
import SurfaceStationMarkers from "./SurfaceStationMarkers";


const KAKAO_APPKEY = import.meta.env.VITE_KAKAO_API_KEY;

export default function MapView({ selectedRegion, onRegionSelect }) {
  const { loaded, error } = useKakaoLoader(KAKAO_APPKEY);
  const mapRef = useRef(null);
  const containerRef = useRef(null);
  const infoWindowRef = useRef(null);
  const touristMarkersRef = useRef([]);
  const marineMarkersRef = useRef([]);
  const surfaceMarkersRef = useRef([]);

  const [places, setPlaces] = useState([]);

  const [marineStations, setMarineStations] = useState([]);
  const [surfaceStations, setSurfaceStations] = useState([]);
  const [marineObservations, setMarineObservations] = useState([]);
  const [surfaceObservations, setSurfaceObservations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedWaterSport, setSelectedWaterSport] = useState(null);

  const [showMarineStations, setShowMarineStations] = useState(false);
  const [showSurfaceStations, setShowSurfaceStations] = useState(false);
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

  // 데이터 가져오기
  const fetchAllData = async () => {
    setLoading(true);


    try {
      const params = {};
      if (selectedWaterSport) {
        params.category_code = selectedWaterSport;

      }



      // 각 API를 개별적으로 호출하여 어느 것이 실패하는지 확인
      let placesData, marineStationsData, surfaceStationsData, marineObsData, surfaceObsData;

      try {
        placesData = await getMapPlaces(params);
      } catch (error) {
        console.error('❌ Places fetch failed:', error);
        placesData = { places: [] };
      }



      try {
        marineStationsData = await getObservationStations({ category: "MARINE" });
      } catch (error) {
        console.error('❌ Marine stations fetch failed:', error);
        marineStationsData = { stations: [] };
      }

      try {
        surfaceStationsData = await getObservationStations({ category: "SURFACE" });
      } catch (error) {
        console.error('❌ Surface stations fetch failed:', error);
        surfaceStationsData = { stations: [] };
      }

      try {
        marineObsData = await getMarineObservations();
      } catch (error) {
        console.error('❌ Marine observations fetch failed:', error);
        marineObsData = { stations: [] };
      }

      try {
        surfaceObsData = await getSurfaceObservations();
      } catch (error) {
        console.error('❌ Surface observations fetch failed:', error);
        surfaceObsData = { stations: [] };
      }

      setPlaces(placesData?.places || []);
      setMarineStations(marineStationsData?.stations || []);
      setSurfaceStations(surfaceStationsData?.stations || []);
      setMarineObservations(marineObsData?.stations || []);
      setSurfaceObservations(surfaceObsData?.stations || []);


    } catch (error) {
      console.error("❌ Unexpected error in fetchAllData:", error);
    } finally {
      setLoading(false);
    }
  };





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

  // 데이터 로드
  useEffect(() => {
    if (loaded) fetchAllData();
  }, [loaded, selectedWaterSport, selectedRegion]);



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
        showMarineStations={showMarineStations}
        onMarineStationsToggle={setShowMarineStations}
        showSurfaceStations={showSurfaceStations}
        onSurfaceStationsToggle={setShowSurfaceStations}
      />

      {/* 마커 컴포넌트들 */}
      <PlaceMarkers
        places={places}
        selectedRegion={selectedRegion}
        mapRef={mapRef}
        touristMarkersRef={touristMarkersRef}
        infoWindowRef={infoWindowRef}
      />

      <MarineStationMarkers
        marineStations={marineStations}
        marineObservations={marineObservations}
        showMarineStations={showMarineStations}
        mapRef={mapRef}
        marineMarkersRef={marineMarkersRef}
        infoWindowRef={infoWindowRef}
      />

      <SurfaceStationMarkers
        surfaceStations={surfaceStations}
        surfaceObservations={surfaceObservations}
        showSurfaceStations={showSurfaceStations}
        mapRef={mapRef}
        surfaceMarkersRef={surfaceMarkersRef}
        infoWindowRef={infoWindowRef}
      />




    </div>
  );
}