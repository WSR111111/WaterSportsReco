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

      // 해당 관측소의 최신 관측 데이터 찾기
      const observation = marineObservations.find(obs => obs.station_id === station.station_id);

      const marineInfoContent = `
        <div style="padding:12px;min-width:280px;font-family:Arial,sans-serif;position:relative;">
          <button onclick="this.parentElement.parentElement.parentElement.style.display='none'" 
                  style="position:absolute;top:8px;right:8px;background:#f8f9fa;border:1px solid #dee2e6;border-radius:50%;width:24px;height:24px;cursor:pointer;font-size:14px;color:#6c757d;display:flex;align-items:center;justify-content:center;">
            ✕
          </button>
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