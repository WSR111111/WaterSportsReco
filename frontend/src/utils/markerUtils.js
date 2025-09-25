// 마커 생성 및 관리 유틸리티

// 마커 생성 헬퍼
export const createMarker = (position, map, markerType = 'default') => {
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
export const isValidCoordinate = (lat, lng) => {
  return !isNaN(lat) && !isNaN(lng) && lat !== 0 && lng !== 0 &&
    lat >= 33 && lat <= 43 && lng >= 124 && lng <= 132;
};

// 관측 데이터 포맷팅
export const formatValue = (value, unit = "") => {
  if (value === null || value === undefined || value === -9 || value === -99) return "결측";
  return `${value}${unit}`;
};