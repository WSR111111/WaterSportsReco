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

      // 해당 관측소의 최신 관측 데이터 찾기
      const observation = surfaceObservations.find(obs => obs.station_id === station.station_id);

      const surfaceInfoContent = `
        <div style="padding:12px;min-width:300px;font-family:Arial,sans-serif;position:relative;">
          <button onclick="this.parentElement.parentElement.parentElement.style.display='none'" 
                  style="position:absolute;top:8px;right:8px;background:#f8f9fa;border:1px solid #dee2e6;border-radius:50%;width:24px;height:24px;cursor:pointer;font-size:14px;color:#6c757d;display:flex;align-items:center;justify-content:center;">
            ✕
          </button>
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