import { useEffect } from 'react';
import { isValidCoordinate } from '../utils/markerUtils';

export default function ObservationStationMarkers({ 
  marineStations,
  surfaceStations,
  marineObservations,
  surfaceObservations,
  showObservationStations,
  mapRef, 
  observationMarkersRef, 
  infoWindowRef 
}) {
  
  // 관측소 마커 표시
  const displayObservationStations = () => {
    console.log('🔍 ObservationStationMarkers - displayObservationStations 호출');
    console.log('📊 Props 상태:', {
      showObservationStations,
      marineStations: marineStations?.length || 0,
      surfaceStations: surfaceStations?.length || 0,
      marineObservations: marineObservations?.length || 0,
      surfaceObservations: surfaceObservations?.length || 0,
      mapRef: !!mapRef.current,
      kakao: !!window.kakao
    });

    if (!mapRef.current || !window.kakao || !showObservationStations) {
      console.log('❌ 조건 불만족으로 마커 표시 중단');
      observationMarkersRef.current.forEach(marker => marker.setMap(null));
      observationMarkersRef.current = [];
      return;
    }

    // 기존 마커 제거
    observationMarkersRef.current.forEach(marker => marker.setMap(null));
    observationMarkersRef.current = [];

    // 해양 관측소와 지상 관측소를 통합
    const allStations = [
      ...(marineStations || []).map(station => ({ ...station, type: 'marine' })),
      ...(surfaceStations || []).map(station => ({ ...station, type: 'surface' }))
    ];
    
    console.log('🏢 통합된 관측소 수:', allStations.length);
    console.log('🏢 관측소 목록:', allStations.slice(0, 3)); // 처음 3개만 로그

    // 관측 데이터를 station_id별로 그룹화
    const observationsByStation = {};
    
    // 해양 관측 데이터 추가
    (marineObservations || []).forEach(obs => {
      if (!observationsByStation[obs.station_id]) {
        observationsByStation[obs.station_id] = [];
      }
      observationsByStation[obs.station_id].push({ ...obs, type: 'marine' });
    });

    // 지상 관측 데이터 추가
    (surfaceObservations || []).forEach(obs => {
      if (!observationsByStation[obs.station_id]) {
        observationsByStation[obs.station_id] = [];
      }
      observationsByStation[obs.station_id].push({ ...obs, type: 'surface' });
    });

    // 모든 관측소 표시 (필터링 제거)
    console.log('🎯 마커 생성 시작, 관측소 수:', allStations.length);
    allStations.forEach((station, index) => {
      const lat = parseFloat(station.latitude || station.lat);
      const lng = parseFloat(station.longitude || station.lon);

      if (!isValidCoordinate(lat, lng)) {
        console.log(`❌ 관측소 ${station.station_id} 좌표 무효:`, { lat, lng });
        return;
      }
      
      if (index < 3) {
        console.log(`✅ 관측소 ${station.station_id} 마커 생성:`, { lat, lng, type: station.type });
      }

      const position = new window.kakao.maps.LatLng(lat, lng);
      
      // 관측소 전용 파란색 마커 생성 (leisure_place와 구분)
      const markerImageSrc = 'https://t1.daumcdn.net/localimg/localimages/07/mapapidoc/marker_blue.png';
      const imageSize = new window.kakao.maps.Size(24, 35);
      const markerImage = new window.kakao.maps.MarkerImage(markerImageSrc, imageSize);
      
      const marker = new window.kakao.maps.Marker({
        position: position,
        image: markerImage,
        map: mapRef.current
      });
      
      if (index < 3) {
        console.log(`🎯 관측소 마커 생성: ${station.station_id} (${station.type === 'marine' ? '해양' : '지상'}) at ${lat}, ${lng}`);
      }

      // 관측 데이터 정리
      const stationObservations = observationsByStation[station.station_id] || [];
      const marineObs = stationObservations.filter(obs => obs.type === 'marine');
      const surfaceObs = stationObservations.filter(obs => obs.type === 'surface');

      // 관측소 타입에 따른 색상과 아이콘 (InfoWindow용)
      const markerColor = station.type === 'marine' ? '#1976d2' : '#dc3545';
      const markerIcon = station.type === 'marine' ? '🌊' : '🏢';
      
      // InfoWindow 내용 생성
      const infoContent = `
        <div style="padding:15px;min-width:300px;max-width:400px;position:relative;">
          <button onclick="this.parentElement.parentElement.parentElement.style.display='none'" 
                  style="position:absolute;top:10px;right:10px;background:#f8f9fa;border:1px solid #dee2e6;border-radius:50%;width:24px;height:24px;cursor:pointer;font-size:14px;color:#6c757d;display:flex;align-items:center;justify-content:center;">
            ✕
          </button>
          
          <h4 style="margin:0 0 10px 0;color:${markerColor};font-size:16px;font-weight:bold;">
            ${markerIcon} ${station.station_nm || station.station_id}
          </h4>
          
          <p style="margin:0 0 5px 0;color:#666;font-size:13px;">
            📍 관측소 ID: ${station.station_id}
          </p>
          
          <p style="margin:0 0 15px 0;color:#666;font-size:13px;">
            🌍 위치: ${lat.toFixed(4)}, ${lng.toFixed(4)}
          </p>

          ${marineObs.length > 0 ? `
            <div style="margin-bottom:15px;">
              <h5 style="margin:0 0 8px 0;color:#1976d2;font-size:14px;font-weight:bold;">
                🌊 해양 관측 데이터
              </h5>
              ${marineObs.map(obs => `
                <div style="margin:5px 0;padding:5px;background:#e3f2fd;border-radius:4px;font-size:12px;">
                  <strong>${obs.obs_name || obs.obs_cd}:</strong> 
                  ${obs.observation_value}${getObservationUnit(obs.obs_cd)}
                  <span style="color:#666;margin-left:8px;">
                    ${obs.observed_at ? new Date(obs.observed_at).toLocaleString('ko-KR') : ''}
                  </span>
                </div>
              `).join('')}
            </div>
          ` : ''}

          ${surfaceObs.length > 0 ? `
            <div style="margin-bottom:10px;">
              <h5 style="margin:0 0 8px 0;color:#dc3545;font-size:14px;font-weight:bold;">
                🏢 지상 관측 데이터
              </h5>
              ${surfaceObs.map(obs => `
                <div style="margin:5px 0;padding:5px;background:#ffebee;border-radius:4px;font-size:12px;">
                  <strong>${obs.obs_name || obs.obs_cd}:</strong> 
                  ${obs.observation_value}${getObservationUnit(obs.obs_cd)}
                  <span style="color:#666;margin-left:8px;">
                    ${obs.observed_at ? new Date(obs.observed_at).toLocaleString('ko-KR') : ''}
                  </span>
                </div>
              `).join('')}
            </div>
          ` : ''}

          ${stationObservations.length === 0 ? `
            <div style="padding:10px;background:#f8f9fa;border-radius:4px;color:#666;font-size:13px;text-align:center;">
              현재 관측 데이터가 없습니다
            </div>
          ` : ''}
        </div>`;

      const infoWindow = new window.kakao.maps.InfoWindow({ content: infoContent });

      // 클릭 이벤트 추가
      window.kakao.maps.event.addListener(marker, 'click', () => {
        if (infoWindowRef.current) infoWindowRef.current.close();
        infoWindow.open(mapRef.current, marker);
        infoWindowRef.current = infoWindow;
      });

      observationMarkersRef.current.push(marker);
    });
  };

  // 관측 단위 반환 함수
  const getObservationUnit = (obsCode) => {
    const units = {
      'obs_ocean_TA': '°C',
      'obs_ocean_TW': '°C', 
      'obs_ocean_WD': '°',
      'obs_ocean_WS': 'm/s',
      'obs_ocean_WH': 'm',
      'obs_ocean_WP': 's',
      'obs_ground_TA': '°C',
      'obs_ground_WD': '°',
      'obs_ground_WS': 'm/s',
      'obs_ground_RN': 'mm'
    };
    return units[obsCode] || '';
  };

  useEffect(() => {
    displayObservationStations();
  }, [
    marineStations, 
    surfaceStations, 
    marineObservations, 
    surfaceObservations, 
    showObservationStations
  ]);

  return null; // 이 컴포넌트는 UI를 렌더링하지 않음
}