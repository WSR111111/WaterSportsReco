import { useState, useEffect } from "react";
import { getSports } from "../api/client";

const REGIONS = [
  { id: "전체", label: "전체", description: "전국 전체 지역" },
  { id: "서울", label: "서울", description: "서울특별시" },
  { id: "부산", label: "부산", description: "부산광역시" },
  { id: "대구", label: "대구", description: "대구광역시" },
  { id: "인천", label: "인천", description: "인천광역시" },
  { id: "광주", label: "광주", description: "광주광역시" },
  { id: "대전", label: "대전", description: "대전광역시" },
  { id: "울산", label: "울산", description: "울산광역시" },
  { id: "세종", label: "세종", description: "세종특별자치시" },
  { id: "경기", label: "경기", description: "경기도" },
  { id: "강원", label: "강원", description: "강원도" },
  { id: "충북", label: "충북", description: "충청북도" },
  { id: "충남", label: "충남", description: "충청남도" },
  { id: "전북", label: "전북", description: "전라북도" },
  { id: "전남", label: "전남", description: "전라남도" },
  { id: "경북", label: "경북", description: "경상북도" },
  { id: "경남", label: "경남", description: "경상남도" },
  { id: "제주", label: "제주", description: "제주특별자치도" }
];

// 기본 카테고리 (DB에서 데이터를 가져오기 전까지 사용)
const DEFAULT_WATERSPORTS_CATEGORIES = [
  { id: "A03030100", label: "윈드서핑/제트스키", description: "윈드서핑과 제트스키 체험장 및 관련 시설" },
  { id: "A03030200", label: "카약/카누", description: "카약, 카누 체험장 및 대여소" },
  { id: "A03030300", label: "요트", description: "요트 체험 및 마리나 시설" },
  { id: "A03030400", label: "스노쿨링/스킨스쿠버다이빙", description: "스노쿨링 및 스쿠버다이빙 체험" },
  { id: "A03030500", label: "민물낚시", description: "민물낚시터 및 관련 시설" },
  { id: "A03030600", label: "바다낚시", description: "바다낚시 및 선상낚시 체험" },
  { id: "A03030700", label: "수영", description: "수영장 및 해수욕장 시설" },
  { id: "A03030800", label: "래프팅", description: "래프팅 체험장 및 관련 시설" }
];

export default function ActivityFilter({ selectedRegion, onRegionSelect, selectedWaterSport, onWaterSportSelect }) {
  const [isRegionOpen, setIsRegionOpen] = useState(false);
  const [isWaterSportOpen, setIsWaterSportOpen] = useState(false);
  const [waterSportsCategories, setWaterSportsCategories] = useState(DEFAULT_WATERSPORTS_CATEGORIES);
  const [loading, setLoading] = useState(false);

  const handleRegionSelect = (regionId) => {
    onRegionSelect(regionId);
    setIsRegionOpen(false);
  };

  const handleWaterSportSelect = (waterSportId) => {
    onWaterSportSelect(waterSportId);
    setIsWaterSportOpen(false);
  };

  // DB에서 스포츠 카테고리 데이터 가져오기
  useEffect(() => {
    const fetchSports = async () => {
      setLoading(true);
      try {
        const response = await getSports();
        if (response?.sports && response.sports.length > 0) {
          const categories = response.sports.map(sport => ({
            id: sport.code,
            label: sport.name,
            description: `${sport.name} 관련 시설 및 체험장`
          }));
          setWaterSportsCategories(categories);
        }
      } catch (error) {
        console.error("❌ Failed to fetch sports categories:", error);
        // 에러 시 기본 카테고리 사용
        setWaterSportsCategories(DEFAULT_WATERSPORTS_CATEGORIES);
      } finally {
        setLoading(false);
      }
    };

    fetchSports();
  }, []);

  const getSelectedRegionLabel = () => {
      const selectedRegionInfo = REGIONS.find(r => r.id === selectedRegion) || REGIONS[0];
      return selectedRegionInfo.label;
  };

  const getSelectedRegionDescription = () => {
      const selectedRegionInfo = REGIONS.find(r => r.id === selectedRegion) || REGIONS[0];
      return selectedRegionInfo.description;
  };

  const getSelectedWaterSportLabel = () => {
      if (!selectedWaterSport) return "전체 수상레포츠";
      const selectedWaterSportInfo = waterSportsCategories.find(w => w.id === selectedWaterSport);
      return selectedWaterSportInfo ? selectedWaterSportInfo.label : "전체 수상레포츠";
  };

  const getSelectedWaterSportDescription = () => {
      if (!selectedWaterSport) return "모든 수상레포츠 관광지 정보";
      const selectedWaterSportInfo = waterSportsCategories.find(w => w.id === selectedWaterSport);
      return selectedWaterSportInfo ? selectedWaterSportInfo.description : "모든 수상레포츠 관광지 정보";
  };

  return (
    <div style={{
      position: "absolute",
      top: "20px",
      left: "20px",
      display: "flex",
      flexDirection: "column",
      gap: "12px",
      zIndex: 100
    }}>
      {/* 지역 선택 박스 */}
      <div style={{
        backgroundColor: "white",
        borderRadius: "8px",
        boxShadow: "0 2px 10px rgba(0,0,0,0.1)",
        minWidth: "280px",
        maxWidth: "300px"
      }}>
        {/* 지역 선택 헤더 */}
        <div style={{
          padding: "10px 15px",
          backgroundColor: "#007bff",
          color: "white",
          borderRadius: "8px 8px 0 0",
          fontSize: "13px",
          fontWeight: "600",
          display: "flex",
          alignItems: "center",
          gap: "8px"
        }}>
          🌍 지역 선택
        </div>

        {/* 지역 드롭다운 */}
        <div style={{ padding: "12px 15px" }}>
          <div style={{ position: "relative" }}>
            <button
              onClick={() => setIsRegionOpen(!isRegionOpen)}
              style={{
                width: "100%",
                padding: "12px 14px",
                border: "1px solid #e1e5e9",
                borderRadius: "8px",
                backgroundColor: "white",
                cursor: "pointer",
                fontSize: "14px",
                textAlign: "left",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                transition: "all 0.2s ease",
                boxShadow: "0 1px 3px rgba(0,0,0,0.1)"
              }}
              onMouseEnter={(e) => {
                e.target.style.borderColor = "#007bff";
                e.target.style.boxShadow = "0 2px 8px rgba(0,123,255,0.15)";
              }}
              onMouseLeave={(e) => {
                e.target.style.borderColor = "#e1e5e9";
                e.target.style.boxShadow = "0 1px 3px rgba(0,0,0,0.1)";
              }}
            >
            <div>
              <div style={{ fontWeight: "500", color: "#333" }}>
                  {getSelectedRegionLabel()}
              </div>
              <div style={{ fontSize: "12px", color: "#666", marginTop: "2px" }}>
                  {getSelectedRegionDescription()}
                </div>
            </div>
            <span style={{ 
              color: "#6c757d", 
              transform: isRegionOpen ? "rotate(180deg)" : "rotate(0deg)",
              transition: "transform 0.2s ease",
              fontSize: "12px",
              fontWeight: "600"
            }}>
              ▼
            </span>
          </button>

            {isRegionOpen && (
              <div style={{
                position: "absolute",
                top: "100%",
                left: 0,
                right: 0,
                backgroundColor: "white",
                border: "1px solid #e1e5e9",
                borderRadius: "8px",
                boxShadow: "0 6px 20px rgba(0,0,0,0.15)",
                zIndex: 1000,
                maxHeight: "240px",
                overflowY: "auto",
                marginTop: "6px"
              }}>
                {REGIONS.map(region => (
                <button
                  key={region.id}
                  onClick={() => handleRegionSelect(region.id)}
                  style={{
                    width: "100%",
                    padding: "12px 14px",
                    border: "none",
                    backgroundColor: selectedRegion === region.id ? "#e3f2fd" : "transparent",
                    cursor: "pointer",
                    fontSize: "14px",
                    textAlign: "left",
                    color: selectedRegion === region.id ? "#1976d2" : "#333",
                    borderBottom: "1px solid #f5f5f5",
                    transition: "all 0.15s ease"
                  }}
                  onMouseEnter={(e) => {
                    if (selectedRegion !== region.id) {
                        e.target.style.backgroundColor = "#f8f9fa";
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (selectedRegion !== region.id) {
                        e.target.style.backgroundColor = "transparent";
                      }
                    }}
                  >
                    <div style={{ fontWeight: "500" }}>{region.label}</div>
                    <div style={{ fontSize: "11px", color: "#666", marginTop: "2px" }}>
                    {region.description}
                  </div>
                </button>
              ))}
              </div>
            )}
          </div>
        </div>
      </div>


      {/* 수상레포츠 카테고리 박스 */}
      <div style={{
        backgroundColor: "white",
        borderRadius: "8px",
        boxShadow: "0 2px 10px rgba(0,0,0,0.1)",
        minWidth: "280px",
        maxWidth: "300px"
      }}>
        {/* 수상레포츠 카테고리 헤더 */}
        <div style={{
          padding: "10px 15px",
          backgroundColor: "#6f42c1",
          color: "white",
          borderRadius: "8px 8px 0 0",
          fontSize: "13px",
          fontWeight: "600",
          display: "flex",
          alignItems: "center",
          gap: "8px"
        }}>
          🏄‍♂️ 수상레포츠 카테고리
        </div>

        {/* 수상레포츠 카테고리 드롭다운 */}
        <div style={{ padding: "12px 15px" }}>
          <div style={{ position: "relative" }}>
            <button
              onClick={() => setIsWaterSportOpen(!isWaterSportOpen)}
              style={{
                width: "100%",
                padding: "12px 14px",
                border: "1px solid #e1e5e9",
                borderRadius: "8px",
                backgroundColor: "white",
                cursor: "pointer",
                fontSize: "14px",
                textAlign: "left",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                transition: "all 0.2s ease",
                boxShadow: "0 1px 3px rgba(0,0,0,0.1)"
              }}
              onMouseEnter={(e) => {
                e.target.style.borderColor = "#6f42c1";
                e.target.style.boxShadow = "0 2px 8px rgba(111,66,193,0.15)";
              }}
              onMouseLeave={(e) => {
                e.target.style.borderColor = "#e1e5e9";
                e.target.style.boxShadow = "0 1px 3px rgba(0,0,0,0.1)";
              }}
            >
              <div>
                <div style={{ fontWeight: "500", color: "#333" }}>
                  {getSelectedWaterSportLabel()}
                </div>
                <div style={{ fontSize: "12px", color: "#666", marginTop: "2px" }}>
                  {getSelectedWaterSportDescription()}
                </div>
              </div>
              <span style={{ 
                color: "#6c757d", 
                transform: isWaterSportOpen ? "rotate(180deg)" : "rotate(0deg)",
                transition: "transform 0.2s ease",
                fontSize: "12px",
                fontWeight: "600"
              }}>
                ▼
              </span>
            </button>

            {isWaterSportOpen && (
              <div style={{
                position: "absolute",
                top: "100%",
                left: 0,
                right: 0,
                backgroundColor: "white",
                border: "1px solid #e1e5e9",
                borderRadius: "8px",
                boxShadow: "0 6px 20px rgba(0,0,0,0.15)",
                zIndex: 1000,
                maxHeight: "280px",
                overflowY: "auto",
                marginTop: "6px"
              }}>
                {/* 전체 수상레포츠 옵션 */}
                <button
                  onClick={() => handleWaterSportSelect(null)}
                  style={{
                    width: "100%",
                    padding: "12px 14px",
                    border: "none",
                    backgroundColor: !selectedWaterSport ? "#f3e5f5" : "transparent",
                    cursor: "pointer",
                    fontSize: "14px",
                    textAlign: "left",
                    color: !selectedWaterSport ? "#4a148c" : "#333",
                    borderBottom: "1px solid #f5f5f5",
                    transition: "all 0.15s ease"
                  }}
                  onMouseEnter={(e) => {
                    if (selectedWaterSport !== null) {
                      e.target.style.backgroundColor = "#f8f9fa";
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (selectedWaterSport !== null) {
                      e.target.style.backgroundColor = "transparent";
                    }
                  }}
                >
                  <div style={{ fontWeight: "500" }}>전체 수상레포츠</div>
                  <div style={{ fontSize: "11px", color: "#666", marginTop: "2px" }}>
                    모든 수상레포츠 관광지 정보
                  </div>
                </button>

                {/* 세부 카테고리 옵션들 */}
                {waterSportsCategories.map(waterSport => (
                <button
                    key={waterSport.id}
                    onClick={() => handleWaterSportSelect(waterSport.id)}
                  style={{
                    width: "100%",
                    padding: "12px 14px",
                    border: "none",
                    backgroundColor: selectedWaterSport === waterSport.id ? "#f3e5f5" : "transparent",
                    cursor: "pointer",
                    fontSize: "14px",
                    textAlign: "left",
                    color: selectedWaterSport === waterSport.id ? "#4a148c" : "#333",
                    borderBottom: "1px solid #f5f5f5",
                    transition: "all 0.15s ease"
                  }}
                  onMouseEnter={(e) => {
                      if (selectedWaterSport !== waterSport.id) {
                        e.target.style.backgroundColor = "#f8f9fa";
                    }
                  }}
                  onMouseLeave={(e) => {
                      if (selectedWaterSport !== waterSport.id) {
                        e.target.style.backgroundColor = "transparent";
                      }
                    }}
                  >
                    <div style={{ fontWeight: "500" }}>{waterSport.label}</div>
                    <div style={{ fontSize: "11px", color: "#666", marginTop: "2px" }}>
                      {waterSport.description}
                  </div>
                </button>
              ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
