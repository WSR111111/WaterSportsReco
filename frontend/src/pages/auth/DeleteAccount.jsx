/**
 * 회원탈퇴 페이지
 */

import React, { useState } from 'react';
import AuthGuard from '../../components/auth/AuthGuard';
import { useAuth } from '../../components/auth/AuthContext';
import { authAPI, handleAPIError } from '../../components/auth/apiClient';

const DeleteAccount = () => {
  const { user, logout } = useAuth();
  
  const [step, setStep] = useState(1); // 1: 안내, 2: 비밀번호 확인, 3: 최종 확인, 4: 완료
  const [password, setPassword] = useState('');
  const [confirmText, setConfirmText] = useState('');
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

  // 비밀번호 확인
  const handlePasswordVerification = async (e) => {
    e.preventDefault();
    
    if (!password) {
      setErrors({ password: '비밀번호를 입력해주세요.' });
      return;
    }
    
    setLoading(true);
    setErrors({});
    
    try {
      const response = await authAPI.verifyPassword(password);
      
      if (response.data.verified) {
        setStep(3); // 최종 확인 단계로
      } else {
        setErrors({ password: '비밀번호가 올바르지 않습니다.' });
      }
    } catch (error) {
      const errorInfo = handleAPIError(error);
      setErrors({ password: errorInfo.message });
    } finally {
      setLoading(false);
    }
  };

  // 계정 삭제 실행
  const handleAccountDeletion = async () => {
    if (confirmText !== '계정삭제') {
      setErrors({ confirm: '"계정삭제"를 정확히 입력해주세요.' });
      return;
    }
    
    setLoading(true);
    setErrors({});
    
    try {
      await authAPI.deleteAccount(password);
      
      setStep(4); // 완료 단계로
      
      // 3초 후 로그아웃 및 메인 페이지로 이동
      setTimeout(async () => {
        await logout();
        window.location.href = '/';
      }, 3000);
      
    } catch (error) {
      const errorInfo = handleAPIError(error);
      setErrors({ general: errorInfo.message });
    } finally {
      setLoading(false);
    }
  };

  // 단계별 렌더링
  const renderStep = () => {
    switch (step) {
      case 1:
        return (
          <div className="step-content">
            <div className="warning-icon">⚠️</div>
            <h2>계정 삭제 안내</h2>
            
            <div className="info-section">
              <h3>삭제되는 정보</h3>
              <ul>
                <li>개인정보 (이름, 이메일)</li>
                <li>계정 생성 및 수정 기록</li>
                <li>모든 로그인 토큰 및 세션</li>
                <li>서비스 이용 기록</li>
              </ul>
            </div>
            
            <div className="info-section">
              <h3>주의사항</h3>
              <ul>
                <li>계정 삭제는 <strong>되돌릴 수 없습니다</strong></li>
                <li>삭제된 데이터는 복구할 수 없습니다</li>
                <li>동일한 이메일로 재가입이 가능합니다</li>
              </ul>
            </div>
            
            <div className="info-section">
              <h3>대안</h3>
              <ul>
                <li>계정을 일시적으로 비활성화하고 싶다면 고객센터에 문의하세요</li>
                <li>특정 데이터만 삭제하고 싶다면 개별 설정을 확인하세요</li>
              </ul>
            </div>
            
            <div className="button-group">
              <button 
                className="cancel-button"
                onClick={() => window.history.back()}
              >
                취소
              </button>
              <button 
                className="continue-button"
                onClick={() => setStep(2)}
              >
                계속 진행
              </button>
            </div>
          </div>
        );
      
      case 2:
        return (
          <div className="step-content">
            <div className="lock-icon">🔒</div>
            <h2>본인 확인</h2>
            <p>계정 삭제를 위해 현재 비밀번호를 입력해주세요.</p>
            
            <form onSubmit={handlePasswordVerification}>
              <div className="form-group">
                <label htmlFor="password">현재 비밀번호</label>
                <input
                  type="password"
                  id="password"
                  value={password}
                  onChange={(e) => {
                    setPassword(e.target.value);
                    if (errors.password) setErrors({});
                  }}
                  className={errors.password ? 'error' : ''}
                  placeholder="비밀번호를 입력해주세요"
                  autoFocus
                />
                {errors.password && <span className="error-text">{errors.password}</span>}
              </div>
              
              <div className="button-group">
                <button 
                  type="button"
                  className="back-button"
                  onClick={() => setStep(1)}
                >
                  이전
                </button>
                <button 
                  type="submit"
                  className="verify-button"
                  disabled={loading}
                >
                  {loading ? '확인 중...' : '확인'}
                </button>
              </div>
            </form>
          </div>
        );
      
      case 3:
        return (
          <div className="step-content">
            <div className="danger-icon">🚨</div>
            <h2>최종 확인</h2>
            <p>정말로 계정을 삭제하시겠습니까?</p>
            
            <div className="final-warning">
              <p><strong>이 작업은 되돌릴 수 없습니다!</strong></p>
              <p>계속하려면 아래 입력란에 <code>계정삭제</code>를 입력해주세요.</p>
            </div>
            
            {errors.general && (
              <div className="error-message">
                {errors.general}
              </div>
            )}
            
            <div className="form-group">
              <input
                type="text"
                value={confirmText}
                onChange={(e) => {
                  setConfirmText(e.target.value);
                  if (errors.confirm) setErrors({});
                }}
                className={errors.confirm ? 'error' : ''}
                placeholder="계정삭제"
                autoFocus
              />
              {errors.confirm && <span className="error-text">{errors.confirm}</span>}
            </div>
            
            <div className="button-group">
              <button 
                className="back-button"
                onClick={() => setStep(2)}
              >
                이전
              </button>
              <button 
                className="delete-button"
                onClick={handleAccountDeletion}
                disabled={loading || confirmText !== '계정삭제'}
              >
                {loading ? '삭제 중...' : '계정 삭제'}
              </button>
            </div>
          </div>
        );
      
      case 4:
        return (
          <div className="step-content">
            <div className="success-icon">✅</div>
            <h2>계정이 삭제되었습니다</h2>
            <p>그동안 서비스를 이용해 주셔서 감사합니다.</p>
            <p>잠시 후 메인 페이지로 이동합니다...</p>
            
            <div className="completion-info">
              <p>모든 개인정보와 관련 데이터가 안전하게 삭제되었습니다.</p>
              <p>동일한 이메일로 언제든지 재가입하실 수 있습니다.</p>
            </div>
          </div>
        );
      
      default:
        return null;
    }
  };

  return (
    <AuthGuard requireAuth={true}>
      <div className="delete-account-container">
        <div className="delete-account-form">
          <div className="progress-bar">
            <div className="progress-steps">
              {[1, 2, 3, 4].map((stepNum) => (
                <div 
                  key={stepNum}
                  className={`progress-step ${step >= stepNum ? 'active' : ''} ${step === stepNum ? 'current' : ''}`}
                >
                  {stepNum}
                </div>
              ))}
            </div>
          </div>
          
          <div className="user-info">
            <p>계정: <strong>{user?.email}</strong></p>
            <p>이름: <strong>{user?.name}</strong></p>
          </div>
          
          {renderStep()}
        </div>
        
        <style jsx>{`
          .delete-account-container {
            min-height: 100vh;
            background: #f8f9fa;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
          }
          
          .delete-account-form {
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            width: 100%;
            max-width: 500px;
            padding: 40px;
          }
          
          .progress-bar {
            margin-bottom: 30px;
          }
          
          .progress-steps {
            display: flex;
            justify-content: center;
            gap: 20px;
          }
          
          .progress-step {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: #e9ecef;
            color: #6c757d;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            transition: all 0.3s;
          }
          
          .progress-step.active {
            background: #28a745;
            color: white;
          }
          
          .progress-step.current {
            background: #007bff;
            color: white;
            transform: scale(1.1);
          }
          
          .user-info {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 30px;
            text-align: center;
          }
          
          .user-info p {
            margin: 5px 0;
            color: #666;
          }
          
          .step-content {
            text-align: center;
          }
          
          .warning-icon, .lock-icon, .danger-icon, .success-icon {
            font-size: 48px;
            margin-bottom: 20px;
          }
          
          .step-content h2 {
            color: #333;
            margin-bottom: 16px;
          }
          
          .step-content p {
            color: #666;
            margin-bottom: 20px;
            line-height: 1.5;
          }
          
          .info-section {
            text-align: left;
            margin-bottom: 25px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
          }
          
          .info-section h3 {
            color: #333;
            margin-bottom: 12px;
            font-size: 16px;
          }
          
          .info-section ul {
            margin: 0;
            padding-left: 20px;
          }
          
          .info-section li {
            margin-bottom: 8px;
            color: #666;
            line-height: 1.4;
          }
          
          .final-warning {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
          }
          
          .final-warning p {
            margin: 8px 0;
            color: #856404;
          }
          
          .final-warning code {
            background: #f8f9fa;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: monospace;
          }
          
          .completion-info {
            background: #d4edda;
            border: 1px solid #c3e6cb;
            padding: 20px;
            border-radius: 8px;
            margin-top: 20px;
          }
          
          .completion-info p {
            margin: 8px 0;
            color: #155724;
          }
          
          .form-group {
            margin-bottom: 20px;
            text-align: left;
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
            border-color: #007bff;
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
          
          .error-message {
            background: #f8d7da;
            color: #721c24;
            padding: 12px;
            border-radius: 6px;
            margin-bottom: 20px;
            border: 1px solid #f5c6cb;
          }
          
          .button-group {
            display: flex;
            gap: 12px;
            justify-content: center;
            margin-top: 30px;
          }
          
          .button-group button {
            padding: 12px 24px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            transition: all 0.2s;
          }
          
          .cancel-button, .back-button {
            background: #6c757d;
            color: white;
          }
          
          .cancel-button:hover, .back-button:hover {
            background: #545b62;
          }
          
          .continue-button, .verify-button {
            background: #007bff;
            color: white;
          }
          
          .continue-button:hover, .verify-button:hover:not(:disabled) {
            background: #0056b3;
          }
          
          .delete-button {
            background: #dc3545;
            color: white;
          }
          
          .delete-button:hover:not(:disabled) {
            background: #c82333;
          }
          
          .delete-button:disabled {
            background: #6c757d;
            cursor: not-allowed;
          }
          
          button:disabled {
            opacity: 0.7;
            cursor: not-allowed;
          }
          
          @media (max-width: 480px) {
            .delete-account-container {
              padding: 10px;
            }
            
            .delete-account-form {
              padding: 20px;
            }
            
            .button-group {
              flex-direction: column;
            }
            
            .progress-steps {
              gap: 10px;
            }
            
            .progress-step {
              width: 35px;
              height: 35px;
            }
          }
        `}</style>
      </div>
    </AuthGuard>
  );
};

export default DeleteAccount;