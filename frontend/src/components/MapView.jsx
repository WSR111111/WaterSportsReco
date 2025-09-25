import { useEffect, useRef, useState } from "react";
import useKakaoLoader from "../hooks/useKakaoLoader";
import { getMapPlaces, getSports, getObservationStations, getMarineObservations, getSurfaceObservations } from "../api/client";
import ActivityFilter from "./ActivityFilter";

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
  const [sports, setSports] = useState([]);
  const [marineStations, setMarineStations] = useState([]);
  const [surfaceStations, setSurfaceStations] = useState([]);
  const [marineObservations, setMarineObservations] = useState([]);
  const [surfaceObservations, setSurfaceObservations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedWaterSport, setSelectedWaterSport] = useState(null);
  const [showPlaces, setShowPlaces] = useState(true);
  const [showMarineStations, setShowMarineStations] = useState(true);
  const [showSurfaceStations, setShowSurfaceStations] = useState(true);
  const [geoData, setGeoData] = useState(null);

  // GeoJSON 데이터 로드
  useEffect(() => {
    fetch('/geo/korea_sido_simple.json')
      .then(response => response.json())
      .then(data => {
        setGeoData(data);
        console.log('✅ GeoJSON data loaded:', data);
      })
      .catch(error => {
        console.error('❌ Failed to load GeoJSON:', error);
      });
  }, []);

  // GeoJSON에서 지역 경계 계산
  const calculateBounds = (coordinates) => {
    let minLat = Infinity, maxLat = -Infinity;
    let minLng = Infinity, maxLng = -Infinity;

    const processCoordinates = (coords) => {
      if (Array.isArray(coords[0])) {
        coords.forEach(processCoordinates);
      } else {
        const [lng, lat] = coords;
        minLat = Math.min(minLat, lat);
        maxLat = Math.max(maxLat, lat);
        minLng = Math.min(minLng, lng);
        maxLng = Math.max(maxLng, lng);
      }
    };

    processCoordinates(coordinates);

    return {
      center: [(minLng + maxLng) / 2, (minLat + maxLat) / 2],
      bounds: { minLat, maxLat, minLng, maxLng }
    };
  };

  // 지역 선택 시 지도 이동 
  const moveToRegion = (regionName) => {
    if (!mapRef.current || !window.kakao) return;

    // 전체 선택 시 한국 전체 보기
    if (!regionName || regionName === "전체") {
      const center = new window.kakao.maps.LatLng(35.9078, 127.7669);
      mapRef.current.setCenter(center);
      mapRef.current.setLevel(13);
      console.log('🗺️ Moved to 전체 (Korea overview)');
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

      console.log(`🗺️ Moved to ${regionName} (${cleanRegionName}):`, {
        center: center,
        level: level,
        bounds: bounds,
        size: maxDiff.toFixed(3)
      });
    } else {
      console.warn(`⚠️ Region not found in GeoJSON: ${regionName} (${cleanRegionName})`);
      console.log('Available regions:', geoData.features.map(f => f.properties.name));
    }
  };

  // 데이터 가져오기
  const fetchAllData = async () => {
    setLoading(true);
    console.log('🔄 Starting data fetch...');
    
    try {
      const params = {};
      if (selectedWaterSport) {
        params.category_code = selectedWaterSport;
        console.log('🎯 Filtering by sport:', selectedWaterSport);
      }
      
      console.log('📡 Calling APIs...');
      
      // 각 API를 개별적으로 호출하여 어느 것이 실패하는지 확인
      let placesData, sportsData, marineStationsData, surfaceStationsData, marineObsData, surfaceObsData;
      
      try {
        console.log('📍 Fetching places from /api/leisure/map/places...');
        placesData = await getMapPlaces(params);
        console.log('✅ Places loaded:', placesData);
      } catch (error) {
        console.error('❌ Places fetch failed:', error);
        placesData = { places: [] };
      }
      
      try {
        console.log('🏃 Fetching sports from /api/sports/list...');
        sportsData = await getSports();
        console.log('✅ Sports loaded:', sportsData);
      } catch (error) {
        console.error('❌ Sports fetch failed:', error);
        sportsData = { sports: [] };
      }
      
      try {
        console.log('🌊 Fetching marine stations from /api/observation/stations...');
        marineStationsData = await getObservationStations({ category: "MARINE" });
        console.log('✅ Marine stations loaded:', marineStationsData);
      } catch (error) {
        console.error('❌ Marine stations fetch failed:', error);
        marineStationsData = { stations: [] };
      }
      
      try {
        console.log('🏢 Fetching surface stations from /api/observation/stations...');
        surfaceStationsData = await getObservationStations({ category: "SURFACE" });
        console.log('✅ Surface stations loaded:', surfaceStationsData);
      } catch (error) {
        console.error('❌ Surface stations fetch failed:', error);
        surfaceStationsData = { stations: [] };
      }
      
      try {
        console.log('🌊📊 Fetching marine observations from /api/observation/marine...');
        marineObsData = await getMarineObservations();
        console.log('✅ Marine observations loaded:', marineObsData);
      } catch (error) {
        console.error('❌ Marine observations fetch failed:', error);
        marineObsData = { stations: [] };
      }
      
      try {
        console.log('🏢📊 Fetching surface observations from /api/observation/surface...');
        surfaceObsData = await getSurfaceObservations();
        console.log('✅ Surface observations loaded:', surfaceObsData);
      } catch (error) {
        console.error('❌ Surface observations fetch failed:', error);
        surfaceObsData = { stations: [] };
      }

      setPlaces(placesData?.places || []);
      setSports(sportsData?.sports || []);
      setMarineStations(marineStationsData?.stations || []);
      setSurfaceStations(surfaceStationsData?.stations || []);
      setMarineObservations(marineObsData?.stations || []);
      setSurfaceObservations(surfaceObsData?.stations || []);
      
      console.log('🎉 All data set in state:', {
        places: placesData?.places?.length || 0,
        sports: sportsData?.sports?.length || 0,
        marineStations: marineStationsData?.stations?.length || 0,
        surfaceStations: surfaceStationsData?.stations?.length || 0,
        marineObservations: marineObsData?.stations?.length || 0,
        surfaceObservations: surfaceObsData?.stations?.length || 0
      });
    } catch (error) {
      console.error("❌ Unexpected error in fetchAllData:", error);
    } finally {
      setLoading(false);
    }
  };

  // 마커 생성 헬퍼
  const createMarker = (position, map, markerType = 'default') => {
    const markerImages = {
      marine: 'data:image/svg+xml;base64,' + btoa(`
        <svg width="20" height="20" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
          <circle cx="10" cy="10" r="8" fill="#1976d2" stroke="white" stroke-width="2"/>
          <circle cx="10" cy="10" r="4" fill="white"/>
        </svg>`),
      surface: 'data:image/svg+xml;base64,' + btoa(`
        <svg width="20" height="20" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
          <polygon points="10,2 18,16 2,16" fill="#dc3545" stroke="white" stroke-width="2"/>
          <circle cx="10" cy="12" r="2" fill="white"/>
        </svg>`)
    };

    const marker = new window.kakao.maps.Marker({
      position,
      map,
      ...(markerImages[markerType] && {
        image: new window.kakao.maps.MarkerImage(
          markerImages[markerType],
          new window.kakao.maps.Size(20, 20),
          { offset: new window.kakao.maps.Point(10, 10) }
        )
      })
    });

    return marker;
  };

  // 좌표 유효성 검사
  const isValidCoordinate = (lat, lng) => {
    return !isNaN(lat) && !isNaN(lng) && lat !== 0 && lng !== 0 &&
      lat >= 33 && lat <= 43 && lng >= 124 && lng <= 132;
  };

  // 지역별 장소 필터링
  const getFilteredPlaces = () => {
    if (!selectedRegion || selectedRegion === "전체") {
      return places;
    }

    return places.filter(place => {
      if (place.address) {
        const address = place.address.toLowerCase();
        const region = selectedRegion.toLowerCase();

        // 지역명 매칭 로직
        const regionMappings = {
          '서울': ['서울'],
          '부산': ['부산'],
          '대구': ['대구'],
          '인천': ['인천'],
          '광주': ['광주'],
          '대전': ['대전'],
          '울산': ['울산'],
          '세종': ['세종'],
          '경기': ['경기'],
          '강원': ['강원'],
          '충북': ['충청북', '충북'],
          '충남': ['충청남', '충남'],
          '전북': ['전라북', '전북', '전북특별자치도'],
          '전남': ['전라남', '전남'],
          '경북': ['경상북', '경북'],
          '경남': ['경상남', '경남'],
          '제주': ['제주']
        };

        const matchTerms = regionMappings[region] || [region];
        return matchTerms.some(term => address.includes(term));
      }
      return false;
    });
  };

  // 장소 마커 표시
  const displayPlaces = () => {
    if (!mapRef.current || !window.kakao || !showPlaces) {
      touristMarkersRef.current.forEach(marker => marker.setMap(null));
      touristMarkersRef.current = [];
      return;
    }

    // 기존 마커 제거
    touristMarkersRef.current.forEach(marker => marker.setMap(null));
    touristMarkersRef.current = [];

    const filteredPlaces = getFilteredPlaces();
    filteredPlaces.forEach(place => {
      const lat = parseFloat(place.latitude);
      const lng = parseFloat(place.longitude);

      if (!isValidCoordinate(lat, lng)) return;

      const position = new window.kakao.maps.LatLng(lat, lng);
      const marker = createMarker(position, mapRef.current);

      const infoContent = `
        <div style="padding:12px;min-width:250px;max-width:300px;">
          <h4 style="margin:0 0 8px 0;color:#333;font-size:14px;font-weight:bold;">
            ${place.place_name || '제목 없음'}
          </h4>
          <p style="margin:0 0 5px 0;color:#666;font-size:12px;">
            📍 ${place.address || '주소 없음'}
          </p>
          ${place.sport_name ? `<p style="margin:0;color:#007bff;font-size:12px;">🏄 ${place.sport_name}</p>` : ''}
          ${place.first_image ? `<img src="${place.first_image}" alt="장소 이미지" style="width:100%;max-width:200px;height:auto;margin-top:8px;border-radius:4px;" onerror="this.style.display='none'">` : ''}
        </div>`;

      const infoWindow = new window.kakao.maps.InfoWindow({ content: infoContent });

      window.kakao.maps.event.addListener(marker, 'click', () => {
        if (infoWindowRef.current) infoWindowRef.current.close();
        infoWindow.open(mapRef.current, marker);
        infoWindowRef.current = infoWindow;
      });

      touristMarkersRef.current.push(marker);
    });
  };

  // 해양관측소 마커 표시
  const displayMarineStations = () => {
    if (!mapRef.current || !window.kakao || !showMarineStations) {
      marineMarkersRef.current.forEach(marker => marker.setMap(null));
      marineMarkersRef.current = [];
      return;
    }

    marineMarkersRef.current.forEach(marker => marker.setMap(null));
    marineMarkersRef.current = [];

    // 관측소 위치와 최신 관측 데이터를 매칭
    marineStations.forEach(station => {
      const lat = parseFloat(station.lat);
      const lng = parseFloat(station.lon);

      if (!isValidCoordinate(lat, lng)) return;

      const position = new window.kakao.maps.LatLng(lat, lng);
      const marker = createMarker(position, mapRef.current, 'marine');

      // 해당 관측소의 최신 관측 데이터 찾기
      const observation = marineObservations.find(obs => obs.station_id === station.station_id);

      const formatValue = (value, unit = "") => {
        if (value === null || value === undefined || value === -9 || value === -99) return "결측";
        return `${value}${unit}`;
      };

      const infoContent = `
        <div style="padding:12px;min-width:280px;font-family:Arial,sans-serif;">
          <h4 style="margin:0 0 8px 0;color:#1976d2;font-size:14px;font-weight:bold;">
            🌊 ${station.station_name || `해양관측소 ${station.station_id}`}
          </h4>
          <div style="font-size:12px;color:#333;">
            ${observation ? `
              <p style="margin:2px 0;"><strong>수온:</strong> ${formatValue(observation.sst, "°C")}</p>
              <p style="margin:2px 0;"><strong>기온:</strong> ${formatValue(observation.temperature, "°C")}</p>
              <p style="margin:2px 0;"><strong>파고:</strong> ${formatValue(observation.wave_height, " m")}</p>
              <p style="margin:2px 0;"><strong>파주기:</strong> ${formatValue(observation.wave_period, " s")}</p>
              <p style="margin:2px 0;"><strong>풍향:</strong> ${formatValue(observation.wave_direction, "°")}</p>
              <p style="margin:2px 0;"><strong>풍속:</strong> ${formatValue(observation.wind_speed, " m/s")}</p>
              <p style="margin:2px 0;"><strong>관측시각:</strong> ${observation.observed_at || "N/A"}</p>
            ` : '<p style="margin:2px 0;color:#999;">관측 데이터 없음</p>'}
          </div>
        </div>`;

      const infoWindow = new window.kakao.maps.InfoWindow({ content: infoContent });

      window.kakao.maps.event.addListener(marker, 'click', () => {
        if (infoWindowRef.current) infoWindowRef.current.close();
        infoWindow.open(mapRef.current, marker);
        infoWindowRef.current = infoWindow;
      });

      marineMarkersRef.current.push(marker);
    });
  };

  // 지상관측소 마커 표시
  const displaySurfaceStations = () => {
    if (!mapRef.current || !window.kakao || !showSurfaceStations) {
      surfaceMarkersRef.current.forEach(marker => marker.setMap(null));
      surfaceMarkersRef.current = [];
      return;
    }

    surfaceMarkersRef.current.forEach(marker => marker.setMap(null));
    surfaceMarkersRef.current = [];

    // 관측소 위치와 최신 관측 데이터를 매칭
    surfaceStations.forEach(station => {
      const lat = parseFloat(station.lat);
      const lng = parseFloat(station.lon);

      if (!isValidCoordinate(lat, lng)) return;

      const position = new window.kakao.maps.LatLng(lat, lng);
      const marker = createMarker(position, mapRef.current, 'surface');

      // 해당 관측소의 최신 관측 데이터 찾기
      const observation = surfaceObservations.find(obs => obs.station_id === station.station_id);

      const formatValue = (value, unit = "") => {
        if (value === null || value === undefined || value === -9 || value === -99) return "결측";
        return `${value}${unit}`;
      };

      const infoContent = `
        <div style="padding:12px;min-width:300px;font-family:Arial,sans-serif;">
          <h4 style="margin:0 0 8px 0;color:#dc3545;font-size:14px;font-weight:bold;">
            🏢 ${station.station_name || `지상관측소 ${station.station_id}`}
          </h4>
          <div style="font-size:12px;color:#333;">
            ${observation ? `
              <p style="margin:2px 0;"><strong>기온:</strong> ${formatValue(observation.temperature, "°C")}</p>
              <p style="margin:2px 0;"><strong>습도:</strong> ${formatValue(observation.humidity, "%")}</p>
              <p style="margin:2px 0;"><strong>풍향:</strong> ${formatValue(observation.wind_direction, "°")}</p>
              <p style="margin:2px 0;"><strong>풍속:</strong> ${formatValue(observation.wind_speed, " m/s")}</p>
              <p style="margin:2px 0;"><strong>기압:</strong> ${formatValue(observation.pressure, " hPa")}</p>
              <p style="margin:2px 0;"><strong>강수량:</strong> ${formatValue(observation.precipitation, " mm")}</p>
              <p style="margin:2px 0;"><strong>관측시각:</strong> ${observation.observed_at || "N/A"}</p>
            ` : '<p style="margin:2px 0;color:#999;">관측 데이터 없음</p>'}
          </div>
        </div>`;

      const infoWindow = new window.kakao.maps.InfoWindow({ content: infoContent });

      window.kakao.maps.event.addListener(marker, 'click', () => {
        if (infoWindowRef.current) infoWindowRef.current.close();
        infoWindow.open(mapRef.current, marker);
        infoWindowRef.current = infoWindow;
      });

      surfaceMarkersRef.current.push(marker);
    });
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

  // 마커 표시
  useEffect(() => {
    displayPlaces();
  }, [places, selectedRegion, showPlaces]);

  useEffect(() => {
    displayMarineStations();
  }, [marineStations, marineObservations, showMarineStations]);

  useEffect(() => {
    displaySurfaceStations();
  }, [surfaceStations, surfaceObservations, showSurfaceStations]);

  // 지역 선택 시 지도 이동
  useEffect(() => {
    if (loaded && mapRef.current) {
      moveToRegion(selectedRegion);
    }
  }, [selectedRegion, loaded]);

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
      />

      {/* 컨트롤 패널 */}
      <div style={{
        position: "absolute", top: "20px", right: "20px", backgroundColor: "white",
        borderRadius: "8px", boxShadow: "0 2px 10px rgba(0,0,0,0.1)", padding: "16px", minWidth: "200px"
      }}>
        <h4 style={{ margin: "0 0 12px 0", fontSize: "14px" }}>표시 옵션</h4>

        <label style={{ display: "flex", alignItems: "center", marginBottom: "8px", cursor: "pointer", fontSize: "13px" }}>
          <input
            type="checkbox"
            checked={showPlaces}
            onChange={(e) => setShowPlaces(e.target.checked)}
            style={{ marginRight: "8px" }}
          />
          �  수상스포츠 장소 ({getFilteredPlaces().length}개)
        </label>

        <label style={{ display: "flex", alignItems: "center", marginBottom: "8px", cursor: "pointer", fontSize: "13px" }}>
          <input
            type="checkbox"
            checked={showMarineStations}
            onChange={(e) => setShowMarineStations(e.target.checked)}
            style={{ marginRight: "8px" }}
          />
          � 지해양관측소 ({marineStations.length}개)
        </label>

        <label style={{ display: "flex", alignItems: "center", marginBottom: "12px", cursor: "pointer", fontSize: "13px" }}>
          <input
            type="checkbox"
            checked={showSurfaceStations}
            onChange={(e) => setShowSurfaceStations(e.target.checked)}
            style={{ marginRight: "8px" }}
          />
          🏢 지상관측소 ({surfaceStations.length}개)
        </label>

        <div style={{ fontSize: "12px", color: "#666", borderTop: "1px solid #eee", paddingTop: "8px", marginBottom: "12px" }}>
          총 데이터: 장소 {places.length}개, 해양 {marineStations.length}개, 지상 {surfaceStations.length}개
        </div>

        <button
          onClick={fetchAllData}
          disabled={loading}
          style={{
            width: "100%", padding: "8px", backgroundColor: "#28a745", color: "white",
            border: "none", borderRadius: "4px", cursor: loading ? "not-allowed" : "pointer", fontSize: "12px"
          }}
        >
          {loading ? "로딩..." : "새로고침"}
        </button>
      </div>

      {loading && (
        <div style={{
          position: "absolute", top: "50%", left: "50%", transform: "translate(-50%, -50%)",
          background: "rgba(0,0,0,0.8)", color: "white", padding: "12px 16px", borderRadius: "8px"
        }}>
          🔄 데이터 로딩 중...
        </div>
      )}
    </div>
  );
}