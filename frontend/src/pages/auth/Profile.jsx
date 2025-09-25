/**
 * 회원정보 수정 페이지
 */

import React, { useState, useEffect } from 'react';
import AuthGuard from '../../components/auth/AuthGuard';
import { useAuth } from '../../components/auth/AuthContext';

const Profile = () => {
  const { user, updateProfile, loading: authLoading } = useAuth();
  
  const [formData, setFormData] = useState({
    name: '',
    password: '',
    confirmPassword: '',
    currentPassword: ''
  });
  
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState('');
  const [activeTab, setActiveTab] = useState('info'); // 'info' or 'password'

  // 사용자 정보로 폼 초기화
  useEffect(() => {
    if (user) {
      setFormData(prev => ({
        ...prev,
        name: user.name || ''
      }));
    }
  }, [user]);

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
    
    // 성공 메시지 제거
    if (success) {
      setSuccess('');
    }
  };

  // 필드 유효성 검사
  const validateField = (name, value) => {
    switch (name) {
      case 'name':
        if (value.length < 2) return '이름은 최소 2자 이상이어야 합니다.';
        if (!/^[가-힣a-zA-Z0-9\s]+$/.test(value)) return '한글, 영문, 숫자만 사용할 수 있습니다.';
        return '';
      
      case 'password':
        if (value && value.length < 8) return '비밀번호는 최소 8자 이상이어야 합니다.';
        if (value && !/[A-Z]/.test(value)) return '대문자가 포함되어야 합니다.';
        if (value && !/[a-z]/.test(value)) return '소문자가 포함되어야 합니다.';
        if (value && !/\d/.test(value)) return '숫자가 포함되어야 합니다.';
        if (value && !/[!@#$%^&*(),.?":{}|<>]/.test(value)) return '특수문자가 포함되어야 합니다.';
        return '';
      
      case 'confirmPassword':
        if (formData.password && value !== formData.password) return '비밀번호가 일치하지 않습니다.';
        return '';
      
      default:
        return '';
    }
  };

  // 정보 수정 폼 유효성 검사
  const validateInfoForm = () => {
    const newErrors = {};
    
    if (!formData.name) {
      newErrors.name = '이름을 입력해주세요.';
    } else {
      const nameError = validateField('name', formData.name);
      if (nameError) newErrors.name = nameError;
    }
    
    if (!formData.currentPassword) {
      newErrors.currentPassword = '현재 비밀번호를 입력해주세요.';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // 비밀번호 변경 폼 유효성 검사
  const validatePasswordForm = () => {
    const newErrors = {};
    
    if (!formData.password) {
      newErrors.password = '새 비밀번호를 입력해주세요.';
    } else {
      const passwordError = validateField('password', formData.password);
      if (passwordError) newErrors.password = passwordError;
    }
    
    if (!formData.confirmPassword) {
      newErrors.confirmPassword = '비밀번호 확인을 입력해주세요.';
    } else {
      const confirmError = validateField('confirmPassword', formData.confirmPassword);
      if (confirmError) newErrors.confirmPassword = confirmError;
    }
    
    if (!formData.currentPassword) {
      newErrors.currentPassword = '현재 비밀번호를 입력해주세요.';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // 정보 수정 처리
  const handleInfoUpdate = async (e) => {
    e.preventDefault();
    
    if (!validateInfoForm()) {
      return;
    }
    
    setLoading(true);
    setErrors({});
    
    try {
      const result = await updateProfile({
        name: formData.name,
        current_password: formData.currentPassword
      });
      
      if (result.success) {
        setSuccess('이름이 성공적으로 수정되었습니다.');
        setFormData(prev => ({ ...prev, currentPassword: '' }));
      } else {
        setErrors({ general: result.error });
      }
    } catch (error) {
      console.error('정보 수정 오류:', error);
      setErrors({ general: '정보 수정 중 오류가 발생했습니다.' });
    } finally {
      setLoading(false);
    }
  };

  // 비밀번호 변경 처리
  const handlePasswordUpdate = async (e) => {
    e.preventDefault();
    
    if (!validatePasswordForm()) {
      return;
    }
    
    setLoading(true);
    setErrors({});
    
    try {
      const result = await updateProfile({
        password: formData.password,
        current_password: formData.currentPassword
      });
      
      if (result.success) {
        setSuccess('비밀번호가 성공적으로 변경되었습니다.');
        setFormData(prev => ({
          ...prev,
          password: '',
          confirmPassword: '',
          currentPassword: ''
        }));
      } else {
        setErrors({ general: result.error });
      }
    } catch (error) {
      console.error('비밀번호 변경 오류:', error);
      setErrors({ general: '비밀번호 변경 중 오류가 발생했습니다.' });
    } finally {
      setLoading(false);
    }
  };

  if (authLoading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner">로딩 중...</div>
      </div>
    );
  }

  return (
    <AuthGuard requireAuth={true}>
      <div className="profile-container">
        <div className="profile-header">
          <h1>회원정보 관리</h1>
          <p>개인정보를 안전하게 관리하세요</p>
        </div>
        
        <div className="profile-content">
          <div className="profile-sidebar">
            <div className="user-info">
              <div className="avatar">
                {user?.name?.charAt(0) || 'U'}
              </div>
              <h3>{user?.name}</h3>
              <p>{user?.email}</p>
              <small>가입일: {new Date(user?.created_at).toLocaleDateString()}</small>
            </div>
            
            <nav className="profile-nav">
              <button 
                className={`nav-item ${activeTab === 'info' ? 'active' : ''}`}
                onClick={() => setActiveTab('info')}
              >
                기본 정보
              </button>
              <button 
                className={`nav-item ${activeTab === 'password' ? 'active' : ''}`}
                onClick={() => setActiveTab('password')}
              >
                비밀번호 변경
              </button>
            </nav>
          </div>
          
          <div className="profile-main">
            {success && (
              <div className="success-message">
                {success}
              </div>
            )}
            
            {errors.general && (
              <div className="error-message">
                {errors.general}
              </div>
            )}
            
            {activeTab === 'info' && (
              <div className="form-section">
                <h2>기본 정보 수정</h2>
                <form onSubmit={handleInfoUpdate}>
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
                      value={user?.email || ''}
                      disabled
                      className="disabled"
                    />
                    <small>이메일은 변경할 수 없습니다.</small>
                  </div>
                  
                  <div className="form-group">
                    <label htmlFor="currentPassword">현재 비밀번호</label>
                    <input
                      type="password"
                      id="currentPassword"
                      name="currentPassword"
                      value={formData.currentPassword}
                      onChange={handleChange}
                      className={errors.currentPassword ? 'error' : ''}
                      placeholder="현재 비밀번호를 입력해주세요"
                    />
                    {errors.currentPassword && <span className="error-text">{errors.currentPassword}</span>}
                  </div>
                  
                  <button 
                    type="submit" 
                    className="submit-button"
                    disabled={loading}
                  >
                    {loading ? '수정 중...' : '정보 수정'}
                  </button>
                </form>
              </div>
            )}
            
            {activeTab === 'password' && (
              <div className="form-section">
                <h2>비밀번호 변경</h2>
                <form onSubmit={handlePasswordUpdate}>
                  <div className="form-group">
                    <label htmlFor="currentPasswordForChange">현재 비밀번호</label>
                    <input
                      type="password"
                      id="currentPasswordForChange"
                      name="currentPassword"
                      value={formData.currentPassword}
                      onChange={handleChange}
                      className={errors.currentPassword ? 'error' : ''}
                      placeholder="현재 비밀번호를 입력해주세요"
                    />
                    {errors.currentPassword && <span className="error-text">{errors.currentPassword}</span>}
                  </div>
                  
                  <div className="form-group">
                    <label htmlFor="password">새 비밀번호</label>
                    <input
                      type="password"
                      id="password"
                      name="password"
                      value={formData.password}
                      onChange={handleChange}
                      className={errors.password ? 'error' : ''}
                      placeholder="새 비밀번호를 입력해주세요"
                    />
                    {errors.password && <span className="error-text">{errors.password}</span>}
                    <div className="password-requirements">
                      <small>
                        • 8자 이상 • 대소문자 포함 • 숫자 포함 • 특수문자 포함
                      </small>
                    </div>
                  </div>
                  
                  <div className="form-group">
                    <label htmlFor="confirmPassword">새 비밀번호 확인</label>
                    <input
                      type="password"
                      id="confirmPassword"
                      name="confirmPassword"
                      value={formData.confirmPassword}
                      onChange={handleChange}
                      className={errors.confirmPassword ? 'error' : ''}
                      placeholder="새 비밀번호를 다시 입력해주세요"
                    />
                    {errors.confirmPassword && <span className="error-text">{errors.confirmPassword}</span>}
                  </div>
                  
                  <button 
                    type="submit" 
                    className="submit-button"
                    disabled={loading}
                  >
                    {loading ? '변경 중...' : '비밀번호 변경'}
                  </button>
                </form>
              </div>
            )}
            
            <div className="danger-zone">
              <h3>위험 구역</h3>
              <p>계정을 삭제하면 모든 데이터가 영구적으로 삭제됩니다.</p>
              <button 
                className="danger-button"
                onClick={() => window.location.href = '/delete-account'}
              >
                계정 삭제
              </button>
            </div>
          </div>
        </div>
        
        <style jsx>{`
          .profile-container {
            min-height: 100vh;
            background: #f8f9fa;
            padding: 20px;
          }
          
          .profile-header {
            text-align: center;
            margin-bottom: 40px;
          }
          
          .profile-header h1 {
            color: #333;
            margin-bottom: 8px;
          }
          
          .profile-header p {
            color: #666;
          }
          
          .profile-content {
            max-width: 1000px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: 300px 1fr;
            gap: 30px;
          }
          
          .profile-sidebar {
            background: white;
            border-radius: 10px;
            padding: 30px;
            height: fit-content;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
          }
          
          .user-info {
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 1px solid #eee;
          }
          
          .avatar {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 32px;
            font-weight: bold;
            margin: 0 auto 16px;
          }
          
          .user-info h3 {
            margin: 0 0 8px 0;
            color: #333;
          }
          
          .user-info p {
            margin: 0 0 8px 0;
            color: #666;
          }
          
          .user-info small {
            color: #999;
          }
          
          .profile-nav {
            display: flex;
            flex-direction: column;
            gap: 8px;
          }
          
          .nav-item {
            padding: 12px 16px;
            border: none;
            background: none;
            text-align: left;
            border-radius: 6px;
            cursor: pointer;
            transition: background-color 0.2s;
            color: #666;
          }
          
          .nav-item:hover {
            background: #f8f9fa;
          }
          
          .nav-item.active {
            background: #667eea;
            color: white;
          }
          
          .profile-main {
            background: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
          }
          
          .form-section h2 {
            margin: 0 0 24px 0;
            color: #333;
          }
          
          .form-group {
            margin-bottom: 20px;
          }
          
          .form-group label {
            display: block;
            margin-bottom: 6px;
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
          
          .form-group input.disabled {
            background: #f8f9fa;
            color: #6c757d;
            cursor: not-allowed;
          }
          
          .form-group small {
            color: #666;
            font-size: 12px;
            margin-top: 4px;
            display: block;
          }
          
          .password-requirements {
            margin-top: 5px;
          }
          
          .password-requirements small {
            color: #666;
            font-size: 11px;
          }
          
          .error-text {
            color: #dc3545;
            font-size: 12px;
            margin-top: 5px;
            display: block;
          }
          
          .success-message {
            background: #d4edda;
            color: #155724;
            padding: 12px;
            border-radius: 6px;
            margin-bottom: 20px;
            border: 1px solid #c3e6cb;
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
            background: #667eea;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 500;
            transition: background-color 0.2s;
          }
          
          .submit-button:hover:not(:disabled) {
            background: #5a6fd8;
          }
          
          .submit-button:disabled {
            opacity: 0.7;
            cursor: not-allowed;
          }
          
          .danger-zone {
            margin-top: 40px;
            padding-top: 30px;
            border-top: 1px solid #eee;
          }
          
          .danger-zone h3 {
            color: #dc3545;
            margin-bottom: 8px;
          }
          
          .danger-zone p {
            color: #666;
            margin-bottom: 16px;
          }
          
          .danger-button {
            background: #dc3545;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
          }
          
          .danger-button:hover {
            background: #c82333;
          }
          
          .loading-container {
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
          }
          
          .loading-spinner {
            font-size: 18px;
            color: #666;
          }
          
          @media (max-width: 768px) {
            .profile-content {
              grid-template-columns: 1fr;
              gap: 20px;
            }
            
            .profile-container {
              padding: 10px;
            }
          }
        `}</style>
      </div>
    </AuthGuard>
  );
};

export default Profile;