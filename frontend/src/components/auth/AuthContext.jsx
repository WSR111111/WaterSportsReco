/**
 * 인증 컨텍스트 - 사용자 상태 관리
 */

import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext({
  user: null,
  isAuthenticated: false,
  loading: true,
  login: () => {},
  logout: () => {},
  updateProfile: () => {},
  refreshToken: () => {},
  checkAuthStatus: () => {}
});

// 토큰 저장소 키
const ACCESS_TOKEN_KEY = 'access_token';
const REFRESH_TOKEN_KEY = 'refresh_token';

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // 인증 상태 계산
  const isAuthenticated = !!user;

  // 토큰 관리 함수들
  const getAccessToken = () => localStorage.getItem(ACCESS_TOKEN_KEY);
  const getRefreshToken = () => localStorage.getItem(REFRESH_TOKEN_KEY);
  
  const setTokens = (accessToken, refreshToken) => {
    localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
    if (refreshToken) {
      localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
    }
  };

  const clearTokens = () => {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
  };

  // API 기본 URL
  const API_BASE_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

  // 사용자 정보 조회
  const fetchUserInfo = async (token) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/auth/me`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      return response.data;
    } catch (error) {
      console.error('사용자 정보 조회 실패:', error);
      return null;
    }
  };

  // 토큰 갱신
  const refreshAccessToken = async () => {
    try {
      const refreshToken = getRefreshToken();
      if (!refreshToken) {
        throw new Error('리프레시 토큰이 없습니다.');
      }

      const response = await axios.post(`${API_BASE_URL}/api/auth/refresh`, {
        refresh_token: refreshToken
      });

      const { access_token } = response.data;
      setTokens(access_token, refreshToken);
      
      return access_token;
    } catch (error) {
      console.error('토큰 갱신 실패:', error);
      clearTokens();
      setUser(null);
      throw error;
    }
  };

  // 로그인
  const login = async (email, password) => {
    try {
      setLoading(true);
      
      const response = await axios.post(`${API_BASE_URL}/api/auth/login`, {
        email,
        password
      });

      const { access_token, refresh_token } = response.data;
      
      // 토큰 저장
      setTokens(access_token, refresh_token);
      
      // 사용자 정보 조회
      const userInfo = await fetchUserInfo(access_token);
      if (userInfo) {
        setUser(userInfo);
        return { success: true, user: userInfo };
      } else {
        throw new Error('사용자 정보 조회 실패');
      }
    } catch (error) {
      console.error('로그인 실패:', error);
      clearTokens();
      
      const errorMessage = error.response?.data?.detail?.message || 
                          error.response?.data?.message || 
                          '로그인에 실패했습니다.';
      
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  // 로그아웃
  const logout = async () => {
    try {
      const refreshToken = getRefreshToken();
      
      // 서버에 로그아웃 요청 (리프레시 토큰 무효화)
      if (refreshToken) {
        try {
          await axios.post(`${API_BASE_URL}/api/auth/logout`, refreshToken);
        } catch (error) {
          console.warn('서버 로그아웃 요청 실패:', error);
        }
      }
    } catch (error) {
      console.error('로그아웃 처리 중 오류:', error);
    } finally {
      // 클라이언트 상태 정리
      clearTokens();
      setUser(null);
    }
  };

  // 회원정보 수정
  const updateProfile = async (updateData) => {
    try {
      const token = getAccessToken();
      if (!token) {
        throw new Error('인증 토큰이 없습니다.');
      }

      const response = await axios.put(`${API_BASE_URL}/api/auth/profile`, updateData, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });

      // 사용자 정보 다시 조회
      const updatedUserInfo = await fetchUserInfo(token);
      if (updatedUserInfo) {
        setUser(updatedUserInfo);
      }

      return { success: true, data: response.data };
    } catch (error) {
      console.error('프로필 업데이트 실패:', error);
      
      const errorMessage = error.response?.data?.detail?.message || 
                          error.response?.data?.message || 
                          '프로필 업데이트에 실패했습니다.';
      
      return { success: false, error: errorMessage };
    }
  };

  // 인증 상태 확인
  const checkAuthStatus = async () => {
    try {
      setLoading(true);
      
      const token = getAccessToken();
      if (!token) {
        setUser(null);
        return;
      }

      // 사용자 정보 조회 시도
      const userInfo = await fetchUserInfo(token);
      
      if (userInfo) {
        setUser(userInfo);
      } else {
        // 토큰이 만료되었을 수 있으므로 갱신 시도
        try {
          const newToken = await refreshAccessToken();
          const refreshedUserInfo = await fetchUserInfo(newToken);
          
          if (refreshedUserInfo) {
            setUser(refreshedUserInfo);
          } else {
            clearTokens();
            setUser(null);
          }
        } catch (refreshError) {
          clearTokens();
          setUser(null);
        }
      }
    } catch (error) {
      console.error('인증 상태 확인 실패:', error);
      clearTokens();
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  // 컴포넌트 마운트 시 인증 상태 확인
  useEffect(() => {
    checkAuthStatus();
  }, []);

  // 토큰 자동 갱신 설정 (선택사항)
  useEffect(() => {
    if (!isAuthenticated) return;

    // 13분마다 토큰 갱신 시도 (15분 만료 전에)
    const interval = setInterval(async () => {
      try {
        await refreshAccessToken();
      } catch (error) {
        console.error('자동 토큰 갱신 실패:', error);
        logout();
      }
    }, 13 * 60 * 1000); // 13분

    return () => clearInterval(interval);
  }, [isAuthenticated]);

  const contextValue = {
    user,
    isAuthenticated,
    loading,
    login,
    logout,
    updateProfile,
    refreshToken: refreshAccessToken,
    checkAuthStatus
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
};

// 커스텀 훅
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth는 AuthProvider 내에서 사용되어야 합니다.');
  }
  return context;
};

export default AuthContext;