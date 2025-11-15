import { useEffect } from 'react';
import { createMarker, isValidCoordinate, formatValue } from '../utils/markerUtils';

export default function MarineStationMarkers({ 
  marineStations, 
  marineObservations, 
  showMarineStations, 
  mapRef, 
  marineMarkersRef, 
  infoWindowRef 
}) {
  
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

      // 해당 관측소의 최신 관측 데이터들 찾기
      const stationData = marineObservations.find(obs => obs.station_id === station.station_id);
      
      console.log(`🌊 해양관측소 ${station.station_id} (${station.station_nm}) 데이터 매칭:`, stationData);
      
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

      const marineInfoContent = `
        <div style="padding:12px;min-width:280px;font-family:Arial,sans-serif;position:relative;">
          <button onclick="this.parentElement.parentElement.parentElement.style.display='none'" 
                  style="position:absolute;top:8px;right:8px;background:#f8f9fa;border:1px solid #dee2e6;border-radius:50%;width:24px;height:24px;cursor:pointer;font-size:14px;color:#6c757d;display:flex;align-items:center;justify-content:center;">
            ✕
          </button>
          <h4 style="margin:0 0 8px 0;color:#1976d2;font-size:14px;font-weight:bold;">
            🌊 ${station.station_nm || `해양관측소 ${station.station_id}`}
          </h4>
          <div style="font-size:12px;color:#333;">
            ${hasData ? `
              ${obsData['obs_ocean_TW'] ? `<p style="margin:2px 0;"><strong>수온:</strong> ${formatValue(obsData['obs_ocean_TW'].value, "°C")}</p>` : ''}
              ${obsData['obs_ocean_WH'] ? `<p style="margin:2px 0;"><strong>파고:</strong> ${formatValue(obsData['obs_ocean_WH'].value, " m")}</p>` : ''}
              ${obsData['obs_ocean_WP'] ? `<p style="margin:2px 0;"><strong>파주기:</strong> ${formatValue(obsData['obs_ocean_WP'].value, " s")}</p>` : ''}
              ${obsData['obs_ocean_WD'] ? `<p style="margin:2px 0;"><strong>풍향:</strong> ${formatValue(obsData['obs_ocean_WD'].value, "°")}</p>` : ''}
              ${obsData['obs_ocean_WS'] ? `<p style="margin:2px 0;"><strong>풍속:</strong> ${formatValue(obsData['obs_ocean_WS'].value, " m/s")}</p>` : ''}
              <p style="margin:4px 0 0 0;font-size:11px;color:#666;"><strong>관측시각:</strong> ${formatTime(latestTime)}</p>
            ` : `
              <p style="margin:2px 0;color:#999;text-align:center;padding:8px;">
                🌊 현재 관측 데이터가 없습니다<br>
                <span style="font-size:11px;">데이터 수집 중이거나 일시적으로 사용할 수 없습니다</span>
              </p>
            `}
          </div>
        </div>`;

      const infoWindow = new window.kakao.maps.InfoWindow({ content: marineInfoContent });

      window.kakao.maps.event.addListener(marker, 'click', () => {
        if (infoWindowRef.current) infoWindowRef.current.close();
        infoWindow.open(mapRef.current, marker);
        infoWindowRef.current = infoWindow;
      });

      marineMarkersRef.current.push(marker);
    });
  };

  useEffect(() => {
    displayMarineStations();
  }, [marineStations, marineObservations, showMarineStations]);

  return null; // 이 컴포넌트는 UI를 렌더링하지 않음
}