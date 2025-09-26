/**
 * API 클라이언트 설정 - axios 인터셉터 및 토큰 관리
 */

import axios from 'axios';

// API 기본 설정
const API_BASE_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

// 토큰 저장소 키
const ACCESS_TOKEN_KEY = 'access_token';
const REFRESH_TOKEN_KEY = 'refresh_token';

// 토큰 관리 함수들
const getAccessToken = () => localStorage.getItem(ACCESS_TOKEN_KEY);
const getRefreshToken = () => localStorage.getItem(REFRESH_TOKEN_KEY);
const setAccessToken = (token) => localStorage.setItem(ACCESS_TOKEN_KEY, token);
const clearTokens = () => {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
};

// axios 인스턴스 생성
const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 토큰 갱신 중인지 확인하는 플래그
let isRefreshing = false;
let failedQueue = [];

// 대기 중인 요청들을 처리하는 함수
const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  
  failedQueue = [];
};

// 요청 인터셉터 - 모든 요청에 토큰 자동 첨부
apiClient.interceptors.request.use(
  (config) => {
    const token = getAccessToken();
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // 요청 로깅 (개발 환경에서만)
    if (import.meta.env.DEV) {
      console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`, {
        headers: config.headers,
        data: config.data
      });
    }
    
    return config;
  },
  (error) => {
    console.error('Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// 응답 인터셉터 - 토큰 만료 시 자동 갱신
apiClient.interceptors.response.use(
  (response) => {
    // 응답 로깅 (개발 환경에서만)
    if (import.meta.env.DEV) {
      console.log(`API Response: ${response.config.method?.toUpperCase()} ${response.config.url}`, {
        status: response.status,
        data: response.data
      });
    }
    
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    
    // 401 에러이고 아직 재시도하지 않은 경우
    if (error.response?.status === 401 && !originalRequest._retry) {
      // 이미 토큰 갱신 중인 경우 대기열에 추가
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then(token => {
          originalRequest.headers.Authorization = `Bearer ${token}`;
          return apiClient(originalRequest);
        }).catch(err => {
          return Promise.reject(err);
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const refreshToken = getRefreshToken();
        
        if (!refreshToken) {
          throw new Error('No refresh token available');
        }

        // 토큰 갱신 요청
        const response = await axios.post(`${API_BASE_URL}/api/auth/refresh`, {
          refresh_token: refreshToken
        });

        const { access_token } = response.data;
        setAccessToken(access_token);
        
        // 대기 중인 요청들 처리
        processQueue(null, access_token);
        
        // 원래 요청 재시도
        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return apiClient(originalRequest);
        
      } catch (refreshError) {
        console.error('Token refresh failed:', refreshError);
        
        // 토큰 갱신 실패 시 로그아웃 처리
        processQueue(refreshError, null);
        clearTokens();
        
        // 로그인 페이지로 리다이렉트
        if (typeof window !== 'undefined') {
          window.location.href = '/login';
        }
        
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    // 에러 로깅
    console.error('API Error:', {
      url: error.config?.url,
      method: error.config?.method,
      status: error.response?.status,
      message: error.response?.data?.detail?.message || error.message
    });

    return Promise.reject(error);
  }
);

// API 함수들
export const authAPI = {
  // 회원가입
  register: (userData) => apiClient.post('/auth/register', userData),
  
  // 로그인
  login: (credentials) => apiClient.post('/auth/login', credentials),
  
  // 로그아웃
  logout: (refreshToken) => apiClient.post('/auth/logout', refreshToken),
  
  // 토큰 갱신
  refreshToken: (refreshToken) => apiClient.post('/auth/refresh', { refresh_token: refreshToken }),
  
  // 현재 사용자 정보
  getCurrentUser: () => apiClient.get('/auth/me'),
  
  // 프로필 업데이트
  updateProfile: (updateData) => apiClient.put('/auth/profile', updateData),
  
  // 계정 삭제
  deleteAccount: (password) => apiClient.delete('/auth/account', { data: { password } }),
  
  // 이메일 중복 확인
  checkEmail: (email) => apiClient.get(`/auth/check-email/${email}`),
  
  // 비밀번호 확인
  verifyPassword: (password) => apiClient.post('/auth/account/verify-password', { password }),
  
  // 토큰 검증
  validateToken: (token) => apiClient.post('/auth/validate-token', { access_token: token })
};

// 에러 처리 유틸리티
export const handleAPIError = (error) => {
  if (error.response) {
    // 서버에서 응답한 에러
    const errorData = error.response.data;
    
    if (errorData.error) {
      return {
        message: errorData.error.message || '알 수 없는 오류가 발생했습니다.',
        code: errorData.error.code,
        details: errorData.error.details
      };
    }
    
    return {
      message: errorData.message || `HTTP ${error.response.status} 오류`,
      code: `HTTP_${error.response.status}`,
      details: {}
    };
  } else if (error.request) {
    // 네트워크 오류
    return {
      message: '네트워크 연결을 확인해주세요.',
      code: 'NETWORK_ERROR',
      details: {}
    };
  } else {
    // 기타 오류
    return {
      message: error.message || '알 수 없는 오류가 발생했습니다.',
      code: 'UNKNOWN_ERROR',
      details: {}
    };
  }
};

// 재시도 로직이 있는 API 호출 함수
export const apiCallWithRetry = async (apiFunction, maxRetries = 3, delay = 1000) => {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await apiFunction();
    } catch (error) {
      if (i === maxRetries - 1) {
        throw error;
      }
      
      // 네트워크 오류나 5xx 오류인 경우에만 재시도
      if (error.code === 'NETWORK_ERROR' || 
          (error.response?.status >= 500 && error.response?.status < 600)) {
        await new Promise(resolve => setTimeout(resolve, delay * (i + 1)));
        continue;
      }
      
      throw error;
    }
  }
};

export default apiClient;