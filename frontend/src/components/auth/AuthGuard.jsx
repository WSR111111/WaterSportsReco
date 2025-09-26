/**
 * 인증 가드 컴포넌트 - 라우트 보호
 */

import React, { useEffect } from 'react';
import { useAuth } from './AuthContext';

const AuthGuard = ({ 
  children, 
  requireAuth = true, 
  redirectTo = '/login',
  fallback = null 
}) => {
  const { isAuthenticated, loading, checkAuthStatus } = useAuth();

  useEffect(() => {
    // 인증 상태가 불확실한 경우 다시 확인
    if (!loading && requireAuth && !isAuthenticated) {
      checkAuthStatus();
    }
  }, [isAuthenticated, loading, requireAuth, checkAuthStatus]);

  // 로딩 중일 때
  if (loading) {
    return (
      <div className="auth-loading">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>인증 상태를 확인하는 중...</p>
        </div>
        <style jsx>{`
          .auth-loading {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 200px;
            flex-direction: column;
          }
          .loading-spinner {
            text-align: center;
          }
          .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #3498db;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 16px;
          }
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    );
  }

  // 인증이 필요한데 인증되지 않은 경우
  if (requireAuth && !isAuthenticated) {
    if (fallback) {
      return fallback;
    }

    // 로그인 페이지로 리다이렉트 안내
    return (
      <div className="auth-required">
        <div className="auth-message">
          <h2>로그인이 필요합니다</h2>
          <p>이 페이지에 접근하려면 로그인이 필요합니다.</p>
          <div className="auth-actions">
            <button 
              onClick={() => window.location.href = redirectTo}
              className="login-button"
            >
              로그인하기
            </button>
            <button 
              onClick={() => window.history.back()}
              className="back-button"
            >
              이전 페이지로
            </button>
          </div>
        </div>
        <style jsx>{`
          .auth-required {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 400px;
            padding: 20px;
          }
          .auth-message {
            text-align: center;
            max-width: 400px;
            padding: 40px;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            background: #f9f9f9;
          }
          .auth-message h2 {
            color: #333;
            margin-bottom: 16px;
          }
          .auth-message p {
            color: #666;
            margin-bottom: 24px;
            line-height: 1.5;
          }
          .auth-actions {
            display: flex;
            gap: 12px;
            justify-content: center;
            flex-wrap: wrap;
          }
          .login-button, .back-button {
            padding: 12px 24px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            transition: background-color 0.2s;
          }
          .login-button {
            background-color: #007bff;
            color: white;
          }
          .login-button:hover {
            background-color: #0056b3;
          }
          .back-button {
            background-color: #6c757d;
            color: white;
          }
          .back-button:hover {
            background-color: #545b62;
          }
        `}</style>
      </div>
    );
  }

  // 인증이 불필요하거나 인증된 경우 자식 컴포넌트 렌더링
  return children;
};

// 로그인이 필요한 페이지를 감싸는 HOC
export const withAuth = (Component, options = {}) => {
  return function AuthenticatedComponent(props) {
    return (
      <AuthGuard requireAuth={true} {...options}>
        <Component {...props} />
      </AuthGuard>
    );
  };
};

// 로그인하지 않은 사용자만 접근 가능한 페이지 (로그인, 회원가입 등)
export const GuestGuard = ({ children, redirectTo = '/' }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="auth-loading">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>인증 상태를 확인하는 중...</p>
        </div>
      </div>
    );
  }

  // 이미 로그인된 사용자는 메인 페이지로 리다이렉트
  if (isAuthenticated) {
    return (
      <div className="already-authenticated">
        <div className="auth-message">
          <h2>이미 로그인되어 있습니다</h2>
          <p>로그인된 상태에서는 이 페이지에 접근할 수 없습니다.</p>
          <button 
            onClick={() => window.location.href = redirectTo}
            className="redirect-button"
          >
            메인 페이지로 이동
          </button>
        </div>
        <style jsx>{`
          .already-authenticated {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 400px;
            padding: 20px;
          }
          .auth-message {
            text-align: center;
            max-width: 400px;
            padding: 40px;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            background: #f9f9f9;
          }
          .auth-message h2 {
            color: #333;
            margin-bottom: 16px;
          }
          .auth-message p {
            color: #666;
            margin-bottom: 24px;
            line-height: 1.5;
          }
          .redirect-button {
            padding: 12px 24px;
            border: none;
            border-radius: 4px;
            background-color: #28a745;
            color: white;
            cursor: pointer;
            font-size: 14px;
            transition: background-color 0.2s;
          }
          .redirect-button:hover {
            background-color: #218838;
          }
        `}</style>
      </div>
    );
  }

  return children;
};

export default AuthGuard;