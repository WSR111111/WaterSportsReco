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

// 지역별 장소 필터링 (개선된 버전)
export const getFilteredPlaces = (places, selectedRegion) => {
  if (!selectedRegion || selectedRegion === "전체") {
    return places;
  }

  console.log(`🔍 지역 필터링: ${selectedRegion}, 전체 장소 수: ${places.length}`);

  const filtered = places.filter(place => {
    // 1. region_name으로 먼저 매칭 (DB에서 제공하는 정확한 지역명)
    if (place.region_name) {
      const regionMatch = place.region_name.includes(selectedRegion);
      if (regionMatch) {
        return true;
      }
    }

    // 2. address로 매칭 (백업 방법)
    if (place.address) {
      const address = place.address.toLowerCase();
      const region = selectedRegion.toLowerCase();

      // 지역명 매칭 로직 (더 포괄적으로 개선)
      const regionMappings = {
        '서울': ['서울특별시', '서울시', '서울'],
        '부산': ['부산광역시', '부산시', '부산'],
        '대구': ['대구광역시', '대구시', '대구'],
        '인천': ['인천광역시', '인천시', '인천'],
        '광주': ['광주광역시', '광주시', '광주'],
        '대전': ['대전광역시', '대전시', '대전'],
        '울산': ['울산광역시', '울산시', '울산'],
        '세종': ['세종특별자치시', '세종시', '세종'],
        '경기': ['경기도', '경기'],
        '강원': ['강원특별자치도', '강원도', '강원'],
        '충북': ['충청북도', '충북'],
        '충남': ['충청남도', '충남'],
        '전북': ['전라북도', '전북특별자치도', '전북'],
        '전남': ['전라남도', '전남'],
        '경북': ['경상북도', '경북'],
        '경남': ['경상남도', '경남'],
        '제주': ['제주특별자치도', '제주도', '제주']
      };

      const matchTerms = regionMappings[region] || [region];
      const addressMatch = matchTerms.some(term => address.includes(term));
      
      if (addressMatch) {
        return true;
      }
    }

    return false;
  });

  console.log(`✅ 필터링 결과: ${filtered.length}개 장소`);
  
  // 디버깅: 필터링된 장소들의 지역 정보 출력
  if (filtered.length > 0) {
    console.log('📍 필터링된 장소들:', filtered.slice(0, 3).map(p => ({
      name: p.place_name,
      region: p.region_name,
      address: p.address
    })));
  }

  return filtered;
};