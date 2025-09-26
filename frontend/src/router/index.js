/**
 * 라우터 설정
 */

// 라우트 정의
export const routes = {
  // 메인 페이지
  home: '/',
  
  // 인증 관련 페이지
  auth: {
    login: '/login',
    register: '/register',
    profile: '/profile',
    deleteAccount: '/delete-account'
  },
  
  // 기타 페이지들 (기존 시스템과 연동)
  // 필요에 따라 추가
};

// 라우트 네비게이션 함수
export const navigate = {
  // 홈으로 이동
  toHome: () => {
    window.location.href = routes.home;
  },
  
  // 로그인 페이지로 이동
  toLogin: (returnUrl = null) => {
    const url = returnUrl ? `${routes.auth.login}?return=${encodeURIComponent(returnUrl)}` : routes.auth.login;
    window.location.href = url;
  },
  
  // 회원가입 페이지로 이동
  toRegister: () => {
    window.location.href = routes.auth.register;
  },
  
  // 프로필 페이지로 이동
  toProfile: () => {
    window.location.href = routes.auth.profile;
  },
  
  // 계정 삭제 페이지로 이동
  toDeleteAccount: () => {
    window.location.href = routes.auth.deleteAccount;
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

// URL 파라미터 파싱 유틸리티
export const getUrlParams = () => {
  const params = new URLSearchParams(window.location.search);
  const result = {};
  
  for (const [key, value] of params.entries()) {
    result[key] = value;
  }
  
  return result;
};

// 현재 경로 확인 유틸리티
export const getCurrentPath = () => {
  return window.location.pathname;
};

// 인증이 필요한 경로인지 확인
export const isAuthRequiredPath = (path = getCurrentPath()) => {
  const authRequiredPaths = [
    routes.auth.profile,
    routes.auth.deleteAccount
  ];
  
  return authRequiredPaths.includes(path);
};

// 게스트 전용 경로인지 확인 (로그인된 사용자는 접근 불가)
export const isGuestOnlyPath = (path = getCurrentPath()) => {
  const guestOnlyPaths = [
    routes.auth.login,
    routes.auth.register
  ];
  
  return guestOnlyPaths.includes(path);
};

// 라우트 가드 설정
export const setupRouteGuards = (authContext) => {
  const { isAuthenticated, loading } = authContext;
  const currentPath = getCurrentPath();
  
  // 로딩 중이면 대기
  if (loading) {
    return 'loading';
  }
  
  // 인증이 필요한 페이지에 미인증 사용자가 접근한 경우
  if (isAuthRequiredPath(currentPath) && !isAuthenticated) {
    navigate.toLogin(currentPath);
    return 'redirect';
  }
  
  // 게스트 전용 페이지에 인증된 사용자가 접근한 경우
  if (isGuestOnlyPath(currentPath) && isAuthenticated) {
    navigate.toHome();
    return 'redirect';
  }
  
  return 'allow';
};

export default {
  routes,
  navigate,
  getUrlParams,
  getCurrentPath,
  isAuthRequiredPath,
  isGuestOnlyPath,
  setupRouteGuards
};