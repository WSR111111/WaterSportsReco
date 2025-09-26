/**
 * 로그인 페이지
 */

import React, { useState } from 'react';
import { GuestGuard } from '../../components/auth/AuthGuard';
import { useAuth } from '../../components/auth/AuthContext';

const Login = () => {
  const { login } = useAuth();
  
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  // 입력값 변경 처리
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // 해당 필드의 에러 제거
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  // 폼 유효성 검사
  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.email) {
      newErrors.email = '이메일을 입력해주세요.';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = '올바른 이메일 형식을 입력해주세요.';
    }
    
    if (!formData.password) {
      newErrors.password = '비밀번호를 입력해주세요.';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // 로그인 처리
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setLoading(true);
    setErrors({});
    
    try {
      const result = await login(formData.email, formData.password);
      
      if (result.success) {
        // 로그인 성공 - AuthContext에서 자동으로 상태 업데이트됨
        // 메인 페이지로 리다이렉트
        window.location.href = '/';
      } else {
        // 로그인 실패
        setErrors({ general: result.error });
      }
    } catch (error) {
      console.error('로그인 오류:', error);
      setErrors({ general: '로그인 중 오류가 발생했습니다.' });
    } finally {
      setLoading(false);
    }
  };

  // Enter 키 처리
  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSubmit(e);
    }
  };

  return (
    <GuestGuard>
      <div className="login-container">
        <div className="login-form">
          <div className="logo-section">
            <h1>🌊 Water Sports</h1>
            <p>수상스포츠 추천 서비스</p>
          </div>
          
          <div className="form-section">
            <h2>로그인</h2>
            
            {errors.general && (
              <div className="error-message">
                {errors.general}
              </div>
            )}
            
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label htmlFor="email">이메일</label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  onKeyPress={handleKeyPress}
                  className={errors.email ? 'error' : ''}
                  placeholder="이메일을 입력해주세요"
                  autoComplete="email"
                />
                {errors.email && <span className="error-text">{errors.email}</span>}
              </div>
              
              <div className="form-group">
                <label htmlFor="password">비밀번호</label>
                <div className="password-input-container">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    id="password"
                    name="password"
                    value={formData.password}
                    onChange={handleChange}
                    onKeyPress={handleKeyPress}
                    className={errors.password ? 'error' : ''}
                    placeholder="비밀번호를 입력해주세요"
                    autoComplete="current-password"
                  />
                  <button
                    type="button"
                    className="password-toggle"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? '🙈' : '👁️'}
                  </button>
                </div>
                {errors.password && <span className="error-text">{errors.password}</span>}
              </div>
              
              <button 
                type="submit" 
                className="submit-button"
                disabled={loading}
              >
                {loading ? '로그인 중...' : '로그인'}
              </button>
            </form>
            
            <div className="form-footer">
              <div className="register-link">
                계정이 없으신가요? <a href="/register">회원가입하기</a>
              </div>
              
              <div className="demo-info">
                <small>
                  <strong>데모 계정:</strong><br/>
                  이메일: demo@example.com<br/>
                  비밀번호: Demo123!@#
                </small>
              </div>
            </div>
          </div>
        </div>
        
        <style jsx>{`
          .login-container {
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
          }
          
          .login-form {
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            overflow: hidden;
            width: 100%;
            max-width: 400px;
          }
          
          .logo-section {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
          }
          
          .logo-section h1 {
            margin: 0 0 8px 0;
            font-size: 28px;
            font-weight: 700;
          }
          
          .logo-section p {
            margin: 0;
            opacity: 0.9;
            font-size: 14px;
          }
          
          .form-section {
            padding: 30px;
          }
          
          .form-section h2 {
            margin: 0 0 24px 0;
            color: #333;
            font-size: 24px;
            text-align: center;
          }
          
          .form-group {
            margin-bottom: 20px;
          }
          
          .form-group label {
            display: block;
            margin-bottom: 6px;
            color: #333;
            font-weight: 500;
            font-size: 14px;
          }
          
          .form-group input {
            width: 100%;
            padding: 14px;
            border: 2px solid #e1e5e9;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s, box-shadow 0.3s;
            box-sizing: border-box;
          }
          
          .form-group input:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
          }
          
          .form-group input.error {
            border-color: #dc3545;
          }
          
          .password-input-container {
            position: relative;
          }
          
          .password-toggle {
            position: absolute;
            right: 12px;
            top: 50%;
            transform: translateY(-50%);
            background: none;
            border: none;
            cursor: pointer;
            font-size: 16px;
            padding: 4px;
          }
          
          .error-text {
            color: #dc3545;
            font-size: 12px;
            margin-top: 6px;
            display: block;
          }
          
          .error-message {
            background: #f8d7da;
            color: #721c24;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 20px;
            border: 1px solid #f5c6cb;
            font-size: 14px;
          }
          
          .submit-button {
            width: 100%;
            padding: 16px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            margin-bottom: 20px;
          }
          
          .submit-button:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
          }
          
          .submit-button:disabled {
            opacity: 0.7;
            cursor: not-allowed;
            transform: none;
          }
          
          .form-footer {
            text-align: center;
          }
          
          .register-link {
            margin-bottom: 20px;
            color: #666;
            font-size: 14px;
          }
          
          .register-link a {
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
          }
          
          .register-link a:hover {
            text-decoration: underline;
          }
          
          .demo-info {
            background: #f8f9fa;
            padding: 12px;
            border-radius: 6px;
            border: 1px solid #e9ecef;
          }
          
          .demo-info small {
            color: #6c757d;
            line-height: 1.4;
          }
          
          @media (max-width: 480px) {
            .login-container {
              padding: 10px;
            }
            
            .logo-section {
              padding: 20px;
            }
            
            .form-section {
              padding: 20px;
            }
            
            .logo-section h1 {
              font-size: 24px;
            }
          }
        `}</style>
      </div>
    </GuestGuard>
  );
};

export default Login;