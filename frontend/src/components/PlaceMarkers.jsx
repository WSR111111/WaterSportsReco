import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { createMarker, isValidCoordinate } from '../utils/markerUtils';
import { getFilteredPlaces } from '../utils/regionUtils';

export default function PlaceMarkers({ 
  places, 
  selectedRegion, 
  mapRef, 
  touristMarkersRef, 
  infoWindowRef 
}) {
  const navigate = useNavigate();
  
  // 장소 마커 표시
  const displayPlaces = () => {
    if (!mapRef.current || !window.kakao) {
      touristMarkersRef.current.forEach(marker => marker.setMap(null));
      touristMarkersRef.current = [];
      return;
    }

    // 기존 마커 제거
    touristMarkersRef.current.forEach(marker => marker.setMap(null));
    touristMarkersRef.current = [];

    // 전역 네비게이션 함수 설정
    window.navigateToPlace = (placeId) => {
      navigate(`/place/${placeId}`);
    };

    const filteredPlaces = getFilteredPlaces(places, selectedRegion);
    filteredPlaces.forEach(place => {
      const lat = parseFloat(place.latitude);
      const lng = parseFloat(place.longitude);

      if (!isValidCoordinate(lat, lng)) return;

      const position = new window.kakao.maps.LatLng(lat, lng);
      const marker = createMarker(position, mapRef.current);

      const infoContent = `
        <div style="padding:12px;min-width:250px;max-width:300px;position:relative;">
          <button onclick="this.parentElement.parentElement.parentElement.style.display='none'" 
                  style="position:absolute;top:8px;right:8px;background:#f8f9fa;border:1px solid #dee2e6;border-radius:50%;width:24px;height:24px;cursor:pointer;font-size:14px;color:#6c757d;display:flex;align-items:center;justify-content:center;">
            ✕
          </button>
          <h4 style="margin:0 0 8px 0;color:#007bff;font-size:14px;font-weight:bold;cursor:pointer;text-decoration:underline;" 
              onclick="window.navigateToPlace('${place.id || place.place_name}')">
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

  useEffect(() => {
    displayPlaces();
  }, [places, selectedRegion]);

  return null; // 이 컴포넌트는 UI를 렌더링하지 않음
}