import { useState } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import MapView from "./components/MapView";
import ChatWindow from "./components/ChatWindow";
import Header from "./components/Header";
import Footer from "./components/Footer";
import PlaceDetail from "./pages/PlaceDetail";

function MainPage() {
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

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<MainPage />} />
        <Route path="/place/:placeId" element={<PlaceDetail />} />
      </Routes>
    </Router>
  );
}
