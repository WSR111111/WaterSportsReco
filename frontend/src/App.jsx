import { useState, useEffect } from "react";

// 페이지 컴포넌트들
import MainPage from "./pages/MainPage";
import PlaceDetail from "./pages/PlaceDetail";

// 인증 관련 컴포넌트
import { AuthProvider } from "./components/auth/AuthContext";
import Login from "./pages/auth/Login";
import Register from "./pages/auth/Register";
import Profile from "./pages/auth/Profile";
import DeleteAccount from "./pages/auth/DeleteAccount";

// 라우터
import { getCurrentPath, isPlaceDetailPage, getPlaceIdFromUrl } from "./router";



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
    // 인증 관련 페이지
    case '/login':
      return <Login />;
    case '/register':
      return <Register />;
    case '/profile':
      return <Profile />;
    case '/delete-account':
      return <DeleteAccount />;
    
    // PlaceDetail 페이지 (동적 라우팅)
    default:
      if (isPlaceDetailPage(currentPath)) {
        const placeId = getPlaceIdFromUrl(currentPath);
        return <PlaceDetail placeId={placeId} />;
      }
      // 메인 페이지 (기본값)
      return <MainPage />;
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
