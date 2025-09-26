import { useAuth } from "./auth/AuthContext";
import { navigate } from "../router";

export default function Header() {
  const { user, isAuthenticated, logout, loading } = useAuth();

  const handleLogout = async () => {
    await logout();
    navigate.toHome();
  };

  return (
    <header style={{
      height: "60px",
      backgroundColor: "#2c3e50",
      color: "white",
      display: "flex",
      alignItems: "center",
      padding: "0 20px",
      boxShadow: "0 2px 4px rgba(0,0,0,0.1)"
    }}>
      <h1 
        style={{ 
          margin: 0, 
          fontSize: "24px", 
          fontWeight: "bold",
          cursor: "pointer"
        }}
        onClick={() => navigate.toHome()}
      >
        🌊 해양 스포츠 추천 시스템
      </h1>
      
      <div style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: "20px" }}>
        <div style={{ fontSize: "14px", opacity: 0.8 }}>
          실시간 해양 정보 기반 추천 서비스
        </div>
        
        {!loading && (
          <nav style={{ display: "flex", alignItems: "center", gap: "15px" }}>
            {isAuthenticated ? (
              <>
                <div style={{ 
                  display: "flex", 
                  alignItems: "center", 
                  gap: "10px",
                  fontSize: "14px"
                }}>
                  <span>안녕하세요, {user?.name}님!</span>
                </div>
                
                <div style={{ display: "flex", gap: "10px" }}>
                  <button
                    onClick={() => navigate.toProfile()}
                    style={{
                      background: "transparent",
                      border: "1px solid rgba(255,255,255,0.3)",
                      color: "white",
                      padding: "6px 12px",
                      borderRadius: "4px",
                      cursor: "pointer",
                      fontSize: "12px",
                      transition: "all 0.2s"
                    }}
                    onMouseOver={(e) => {
                      e.target.style.backgroundColor = "rgba(255,255,255,0.1)";
                    }}
                    onMouseOut={(e) => {
                      e.target.style.backgroundColor = "transparent";
                    }}
                  >
                    내 정보
                  </button>
                  
                  <button
                    onClick={handleLogout}
                    style={{
                      background: "rgba(231, 76, 60, 0.8)",
                      border: "1px solid rgba(231, 76, 60, 0.8)",
                      color: "white",
                      padding: "6px 12px",
                      borderRadius: "4px",
                      cursor: "pointer",
                      fontSize: "12px",
                      transition: "all 0.2s"
                    }}
                    onMouseOver={(e) => {
                      e.target.style.backgroundColor = "#e74c3c";
                    }}
                    onMouseOut={(e) => {
                      e.target.style.backgroundColor = "rgba(231, 76, 60, 0.8)";
                    }}
                  >
                    로그아웃
                  </button>
                </div>
              </>
            ) : (
              <div style={{ display: "flex", gap: "10px" }}>
                <button
                  onClick={() => navigate.toLogin()}
                  style={{
                    background: "transparent",
                    border: "1px solid rgba(255,255,255,0.3)",
                    color: "white",
                    padding: "6px 12px",
                    borderRadius: "4px",
                    cursor: "pointer",
                    fontSize: "12px",
                    transition: "all 0.2s"
                  }}
                  onMouseOver={(e) => {
                    e.target.style.backgroundColor = "rgba(255,255,255,0.1)";
                  }}
                  onMouseOut={(e) => {
                    e.target.style.backgroundColor = "transparent";
                  }}
                >
                  로그인
                </button>
                
                <button
                  onClick={() => navigate.toRegister()}
                  style={{
                    background: "rgba(52, 152, 219, 0.8)",
                    border: "1px solid rgba(52, 152, 219, 0.8)",
                    color: "white",
                    padding: "6px 12px",
                    borderRadius: "4px",
                    cursor: "pointer",
                    fontSize: "12px",
                    transition: "all 0.2s"
                  }}
                  onMouseOver={(e) => {
                    e.target.style.backgroundColor = "#3498db";
                  }}
                  onMouseOut={(e) => {
                    e.target.style.backgroundColor = "rgba(52, 152, 219, 0.8)";
                  }}
                >
                  회원가입
                </button>
              </div>
            )}
          </nav>
        )}
      </div>
    </header>
  );
}
