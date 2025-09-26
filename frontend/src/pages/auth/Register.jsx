/**
 * 회원가입 페이지
 */

import React, { useState } from 'react';
import { GuestGuard } from '../../components/auth/AuthGuard';
import { authAPI, handleAPIError } from '../../components/auth/apiClient';

const Register = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    name: ''
  });
  
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

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

  // 실시간 유효성 검사
  const validateField = (name, value) => {
    switch (name) {
      case 'email':
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(value) ? '' : '올바른 이메일 형식을 입력해주세요.';
      
      case 'password':
        if (value.length < 8) return '비밀번호는 최소 8자 이상이어야 합니다.';
        if (!/[A-Z]/.test(value)) return '대문자가 포함되어야 합니다.';
        if (!/[a-z]/.test(value)) return '소문자가 포함되어야 합니다.';
        if (!/\d/.test(value)) return '숫자가 포함되어야 합니다.';
        if (!/[!@#$%^&*(),.?":{}|<>]/.test(value)) return '특수문자가 포함되어야 합니다.';
        return '';
      
      case 'confirmPassword':
        return value === formData.password ? '' : '비밀번호가 일치하지 않습니다.';
      
      case 'name':
        if (value.length < 2) return '이름은 최소 2자 이상이어야 합니다.';
        if (!/^[가-힣a-zA-Z0-9\s]+$/.test(value)) return '한글, 영문, 숫자만 사용할 수 있습니다.';
        return '';
      
      default:
        return '';
    }
  };

  // 폼 유효성 검사
  const validateForm = () => {
    const newErrors = {};
    
    Object.keys(formData).forEach(key => {
      const error = validateField(key, formData[key]);
      if (error) newErrors[key] = error;
    });
    
    // 필수 필드 확인
    if (!formData.email) newErrors.email = '이메일을 입력해주세요.';
    if (!formData.password) newErrors.password = '비밀번호를 입력해주세요.';
    if (!formData.confirmPassword) newErrors.confirmPassword = '비밀번호 확인을 입력해주세요.';
    if (!formData.name) newErrors.name = '이름을 입력해주세요.';
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // 이메일 중복 확인
  const checkEmailAvailability = async (email) => {
    try {
      const response = await authAPI.checkEmail(email);
      return response.data.available;
    } catch (error) {
      console.error('이메일 확인 오류:', error);
      return false;
    }
  };

  // 회원가입 처리
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setLoading(true);
    setErrors({});
    
    try {
      // 이메일 중복 확인
      const emailAvailable = await checkEmailAvailability(formData.email);
      if (!emailAvailable) {
        setErrors({ email: '이미 사용 중인 이메일입니다.' });
        setLoading(false);
        return;
      }
      
      // 회원가입 요청
      const response = await authAPI.register({
        email: formData.email,
        password: formData.password,
        name: formData.name
      });
      
      setSuccess(true);
      
      // 3초 후 로그인 페이지로 이동
      setTimeout(() => {
        window.location.href = '/login';
      }, 3000);
      
    } catch (error) {
      const errorInfo = handleAPIError(error);
      
      if (errorInfo.code === 'EMAIL_ALREADY_EXISTS') {
        setErrors({ email: errorInfo.message });
      } else if (errorInfo.details?.validation_errors) {
        const validationErrors = {};
        errorInfo.details.validation_errors.forEach(err => {
          validationErrors[err.loc[err.loc.length - 1]] = err.msg;
        });
        setErrors(validationErrors);
      } else {
        setErrors({ general: errorInfo.message });
      }
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <GuestGuard>
        <div className="register-success">
          <div className="success-message">
            <div className="success-icon">✅</div>
            <h2>회원가입이 완료되었습니다!</h2>
            <p>환영합니다, {formData.name}님!</p>
            <p>잠시 후 로그인 페이지로 이동합니다...</p>
            <button 
              onClick={() => window.location.href = '/login'}
              className="login-button"
            >
              지금 로그인하기
            </button>
          </div>
        </div>
      </GuestGuard>
    );
  }

  return (
    <GuestGuard>
      <div className="register-container">
        <div className="register-form">
          <h1>회원가입</h1>
          <p className="subtitle">수상스포츠 추천 서비스에 오신 것을 환영합니다!</p>
          
          {errors.general && (
            <div className="error-message general-error">
              {errors.general}
            </div>
          )}
          
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="name">이름</label>
              <input
                type="text"
                id="name"
                name="name"
                value={formData.name}
                onChange={handleChange}
                className={errors.name ? 'error' : ''}
                placeholder="이름을 입력해주세요"
              />
              {errors.name && <span className="error-text">{errors.name}</span>}
            </div>
            
            <div className="form-group">
              <label htmlFor="email">이메일</label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                className={errors.email ? 'error' : ''}
                placeholder="이메일을 입력해주세요"
              />
              {errors.email && <span className="error-text">{errors.email}</span>}
            </div>
            
            <div className="form-group">
              <label htmlFor="password">비밀번호</label>
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                className={errors.password ? 'error' : ''}
                placeholder="비밀번호를 입력해주세요"
              />
              {errors.password && <span className="error-text">{errors.password}</span>}
              <div className="password-requirements">
                <small>
                  • 8자 이상 • 대소문자 포함 • 숫자 포함 • 특수문자 포함
                </small>
              </div>
            </div>
            
            <div className="form-group">
              <label htmlFor="confirmPassword">비밀번호 확인</label>
              <input
                type="password"
                id="confirmPassword"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleChange}
                className={errors.confirmPassword ? 'error' : ''}
                placeholder="비밀번호를 다시 입력해주세요"
              />
              {errors.confirmPassword && <span className="error-text">{errors.confirmPassword}</span>}
            </div>
            
            <button 
              type="submit" 
              className="submit-button"
              disabled={loading}
            >
              {loading ? '가입 중...' : '회원가입'}
            </button>
          </form>
          
          <div className="login-link">
            이미 계정이 있으신가요? <a href="/login">로그인하기</a>
          </div>
        </div>
        
        <style jsx>{`
          .register-container {
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
          }
          
          .register-form {
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
            width: 100%;
            max-width: 400px;
          }
          
          .register-form h1 {
            text-align: center;
            margin-bottom: 8px;
            color: #333;
            font-size: 28px;
          }
          
          .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
            font-size: 14px;
          }
          
          .form-group {
            margin-bottom: 20px;
          }
          
          .form-group label {
            display: block;
            margin-bottom: 5px;
            color: #333;
            font-weight: 500;
          }
          
          .form-group input {
            width: 100%;
            padding: 12px;
            border: 2px solid #e1e5e9;
            border-radius: 6px;
            font-size: 16px;
            transition: border-color 0.3s;
            box-sizing: border-box;
          }
          
          .form-group input:focus {
            outline: none;
            border-color: #667eea;
          }
          
          .form-group input.error {
            border-color: #dc3545;
          }
          
          .error-text {
            color: #dc3545;
            font-size: 12px;
            margin-top: 5px;
            display: block;
          }
          
          .password-requirements {
            margin-top: 5px;
          }
          
          .password-requirements small {
            color: #666;
            font-size: 11px;
          }
          
          .error-message {
            background: #f8d7da;
            color: #721c24;
            padding: 12px;
            border-radius: 6px;
            margin-bottom: 20px;
            border: 1px solid #f5c6cb;
          }
          
          .submit-button {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
          }
          
          .submit-button:hover:not(:disabled) {
            transform: translateY(-2px);
          }
          
          .submit-button:disabled {
            opacity: 0.7;
            cursor: not-allowed;
          }
          
          .login-link {
            text-align: center;
            margin-top: 20px;
            color: #666;
          }
          
          .login-link a {
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
          }
          
          .login-link a:hover {
            text-decoration: underline;
          }
          
          .register-success {
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          }
          
          .success-message {
            background: white;
            padding: 40px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
            max-width: 400px;
          }
          
          .success-icon {
            font-size: 48px;
            margin-bottom: 20px;
          }
          
          .success-message h2 {
            color: #28a745;
            margin-bottom: 16px;
          }
          
          .success-message p {
            color: #666;
            margin-bottom: 12px;
          }
          
          .login-button {
            background: #28a745;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            cursor: pointer;
            margin-top: 20px;
            font-size: 14px;
          }
          
          .login-button:hover {
            background: #218838;
          }
        `}</style>
      </div>
    </GuestGuard>
  );
};

export default Register;