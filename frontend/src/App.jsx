import { useState, useEffect } from "react";
import MapView from "./components/MapView";
import ChatWindow from "./components/ChatWindow";
import MarineDataView from "./components/MarineDataView";
import Header from "./components/Header";
import Footer from "./components/Footer";

// 인증 관련 컴포넌트
import { AuthProvider } from "./components/auth/AuthContext";
import Login from "./pages/auth/Login";
import Register from "./pages/auth/Register";
import Profile from "./pages/auth/Profile";
import DeleteAccount from "./pages/auth/DeleteAccount";

// 라우터
import { getCurrentPath } from "./router";

// 메인 앱 컴포넌트
function MainApp() {
  const [selectedRegion, setSelectedRegion] = useState("전체");
  
  return (
    <div style={{ 
      display: "flex", 
      flexDirection: "column", 
      height: "100vh",
      overflow: "hidden"
    }}>
      <Header />
      
      <main style={{ 
        flex: 1, 
        display: "flex",
        overflow: "hidden",
        position: "relative"
      }}>
        {/* 왼쪽: 지도 */}
        <div style={{ 
          flex: 1,
          position: "relative",
          overflow: "hidden",
          minWidth: 0  // flex 아이템이 축소될 수 있도록
        }}>
          <MapView selectedRegion={selectedRegion} onRegionSelect={setSelectedRegion} />
          
          {/* 해양 데이터 패널 */}
          <div style={{
            position: "absolute",
            top: "20px",
            left: "320px",
            width: "350px",
            maxHeight: "500px",
            backgroundColor: "white",
            borderRadius: "12px",
            boxShadow: "0 4px 20px rgba(0,0,0,0.15)",
            zIndex: 10,
            overflow: "hidden"
          }}>
            <MarineDataView />
          </div>
        </div>
        
        {/* 오른쪽: 채팅창 */}
        <div style={{ 
          width: "400px",
          minWidth: "300px",
          maxWidth: "500px",
          borderLeft: "1px solid #ddd",
          overflow: "hidden",
          display: "flex",
          flexDirection: "column"
        }}>
          <ChatWindow selectedRegion={selectedRegion} />
        </div>
      </main>
      
      <Footer />
    </div>
  );
}

// 라우터 컴포넌트
function AppRouter() {
  const [currentPath, setCurrentPath] = useState(getCurrentPath());
  
  useEffect(() => {
    // URL 변경 감지
    const handlePopState = () => {
      setCurrentPath(getCurrentPath());
    };
    
    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);
  
  // 경로에 따른 컴포넌트 렌더링
  switch (currentPath) {
    case '/login':
      return <Login />;
    case '/register':
      return <Register />;
    case '/profile':
      return <Profile />;
    case '/delete-account':
      return <DeleteAccount />;
    default:
      return <MainApp />;
  }
}

// 최상위 App 컴포넌트
export default function App() {
  return (
    <AuthProvider>
      <AppRouter />
    </AuthProvider>
  );
}
