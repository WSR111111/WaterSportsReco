// 지역 관련 유틸리티

// GeoJSON에서 지역 경계 계산
export const calculateBounds = (coordinates) => {
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

// 지역별 장소 필터링
export const getFilteredPlaces = (places, selectedRegion) => {
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