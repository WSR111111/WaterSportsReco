/**
 * PlaceDetail 페이지 라우터 설정
 */

// PlaceDetail 라우트 정의
export const placeDetailRoutes = {
  detail: '/place/:id',
  detailBase: '/place'
};

// PlaceDetail 네비게이션 함수
export const placeDetailNavigate = {
  // 특정 장소 상세 페이지로 이동
  toPlaceDetail: (placeId) => {
    window.location.href = `/place/${placeId}`;
  },
  
  // 장소 목록으로 이동 (메인 페이지)
  toPlaceList: () => {
    window.location.href = '/';
  },
  
  // 이전 페이지로 이동
  back: () => {
    window.history.back();
  },
  
  // 특정 URL로 이동
  to: (url) => {
    window.location.href = url;
  }
};

// URL에서 장소 ID 추출
export const getPlaceIdFromUrl = (path = window.location.pathname) => {
  const match = path.match(/^\/place\/(.+)$/);
  return match ? match[1] : null;
};

// PlaceDetail 페이지인지 확인
export const isPlaceDetailPage = (path = window.location.pathname) => {
  return path.startsWith('/place/');
};

export default {
  placeDetailRoutes,
  placeDetailNavigate,
  getPlaceIdFromUrl,
  isPlaceDetailPage
};