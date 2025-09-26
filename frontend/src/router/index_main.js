/**
 * 메인 페이지 라우터 설정
 */

// 메인 페이지 라우트 정의
export const mainRoutes = {
  home: '/',
  main: '/main'
};

// 메인 페이지 네비게이션 함수
export const mainNavigate = {
  // 홈으로 이동
  toHome: () => {
    window.location.href = mainRoutes.home;
  },
  
  // 메인 페이지로 이동
  toMain: () => {
    window.location.href = mainRoutes.main;
  },
  
  // 특정 URL로 이동
  to: (url) => {
    window.location.href = url;
  }
};

// 메인 페이지 관련 유틸리티
export const isMainPage = (path = window.location.pathname) => {
  return path === mainRoutes.home || path === mainRoutes.main;
};

export default {
  mainRoutes,
  mainNavigate,
  isMainPage
};