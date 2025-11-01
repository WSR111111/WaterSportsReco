import { useEffect } from 'react';
import { createMarker, isValidCoordinate, formatValue } from '../utils/markerUtils';

export default function SurfaceStationMarkers({ 
  surfaceStations, 
  surfaceObservations, 
  showSurfaceStations, 
  mapRef, 
  surfaceMarkersRef, 
  infoWindowRef 
}) {
  
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

      // 해당 관측소의 최신 관측 데이터들 찾기
      const stationData = surfaceObservations.find(obs => obs.station_id === station.station_id);
      
      console.log(`🏢 지상관측소 ${station.station_id} (${station.station_nm}) 데이터 매칭:`, stationData);
      
      // 관측 항목별로 그룹화
      const obsData = {};
      if (stationData && stationData.observations && Array.isArray(stationData.observations)) {
        stationData.observations.forEach(item => {
          if (item && item.obs_cd) {
            obsData[item.obs_cd] = {
              value: item.observation_value,
              observed_at: item.observed_at,
              name: item.obs_name
            };
            console.log(`  📊 ${item.obs_cd}: ${item.observation_value} (${item.obs_name})`);
          }
        });
      } else {
        console.log(`  ⚠️ 관측소 ${station.station_id}에 대한 관측 데이터가 없습니다`);
      }

      // 관측 데이터 표시 내용 생성
      const hasData = Object.keys(obsData).length > 0;
      const latestTime = hasData ? Object.values(obsData)[0]?.observed_at : null;
      
      // 시간 포맷팅
      const formatTime = (timeStr) => {
        if (!timeStr) return "N/A";
        try {
          const date = new Date(timeStr);
          return date.toLocaleString('ko-KR', {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
          });
        } catch {
          return timeStr;
        }
      };

      const surfaceInfoContent = `
        <div style="padding:12px;min-width:300px;font-family:Arial,sans-serif;position:relative;">
          <button onclick="this.parentElement.parentElement.parentElement.style.display='none'" 
                  style="position:absolute;top:8px;right:8px;background:#f8f9fa;border:1px solid #dee2e6;border-radius:50%;width:24px;height:24px;cursor:pointer;font-size:14px;color:#6c757d;display:flex;align-items:center;justify-content:center;">
            ✕
          </button>
          <h4 style="margin:0 0 8px 0;color:#dc3545;font-size:14px;font-weight:bold;">
            🏢 ${station.station_nm || `지상관측소 ${station.station_id}`}
          </h4>
          <div style="font-size:12px;color:#333;">
            ${hasData ? `
              ${obsData['obs_ground_TA'] ? `<p style="margin:2px 0;"><strong>기온:</strong> ${formatValue(obsData['obs_ground_TA'].value, "°C")}</p>` : ''}
              ${obsData['obs_ground_WD'] ? `<p style="margin:2px 0;"><strong>풍향:</strong> ${formatValue(obsData['obs_ground_WD'].value, "°")}</p>` : ''}
              ${obsData['obs_ground_WS'] ? `<p style="margin:2px 0;"><strong>풍속:</strong> ${formatValue(obsData['obs_ground_WS'].value, " m/s")}</p>` : ''}
              ${obsData['obs_ground_RN'] ? `<p style="margin:2px 0;"><strong>강수량:</strong> ${formatValue(obsData['obs_ground_RN'].value, " mm")}</p>` : ''}
              <p style="margin:4px 0 0 0;font-size:11px;color:#666;"><strong>관측시각:</strong> ${formatTime(latestTime)}</p>
            ` : `
              <p style="margin:2px 0;color:#999;text-align:center;padding:8px;">
                📊 현재 관측 데이터가 없습니다<br>
                <span style="font-size:11px;">데이터 수집 중이거나 일시적으로 사용할 수 없습니다</span>
              </p>
            `}
          </div>
        </div>`;

      const surfaceInfoWindow = new window.kakao.maps.InfoWindow({ content: surfaceInfoContent });

      window.kakao.maps.event.addListener(marker, 'click', () => {
        if (infoWindowRef.current) infoWindowRef.current.close();
        surfaceInfoWindow.open(mapRef.current, marker);
        infoWindowRef.current = surfaceInfoWindow;
      });

      surfaceMarkersRef.current.push(marker);
    });
  };

  useEffect(() => {
    displaySurfaceStations();
  }, [surfaceStations, surfaceObservations, showSurfaceStations]);

  return null; // 이 컴포넌트는 UI를 렌더링하지 않음
}