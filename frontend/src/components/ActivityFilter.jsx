import { useState, useEffect } from "react";
import { getSports } from "../api/client";

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
  const [regions, setRegions] = useState([]);
  const [waterSportsCategories, setWaterSportsCategories] = useState(DEFAULT_WATERSPORTS_CATEGORIES);
  const [loading, setLoading] = useState(true);

  const handleRegionSelect = (regionId) => {
    onRegionSelect(regionId);
    setIsRegionOpen(false);
  };

  const handleWaterSportSelect = (waterSportId) => {
    onWaterSportSelect(waterSportId);
    setIsWaterSportOpen(false);
  };

  // 지역 데이터 가져오기 (GeoJSON 기준)
  useEffect(() => {
    const loadRegions = async () => {
      try {
        // GeoJSON 데이터 로드
        const geoResponse = await fetch('/geo/korea_sido_simple.json');
        const geoData = await geoResponse.json();
        
        console.log("📥 GeoJSON regions:", geoData.features.map(f => f.properties.name));
        
        // GeoJSON의 지역명을 기준으로 리스트 생성
        const regionsList = [
          { id: "전체", label: "전체", description: "전국 전체 지역" },
          ...geoData.features.map(feature => ({
            id: feature.properties.name,
            label: feature.properties.name,
            description: `${feature.properties.name}`
          }))
        ];
        
        setRegions(regionsList);
        console.log("✅ GeoJSON regions loaded:", regionsList.length - 1, "지역");
        setLoading(false);
      } catch (err) {
        console.error("GeoJSON 로드 실패:", err);
        setRegions([{ id: "전체", label: "전체", description: "전국 전체 지역" }]);
        setLoading(false);
      }
    };
    
    loadRegions();
  }, []);

  // 스포츠 카테고리 데이터 가져오기
  useEffect(() => {
    const fetchSports = async () => {
      try {
        const sportsResponse = await getSports();
        if (sportsResponse?.sports && sportsResponse.sports.length > 0) {
          const categories = sportsResponse.sports.map(sport => ({
            id: sport.code,
            label: sport.name,
            description: `${sport.name} 관련 시설 및 체험장`
          }));
          setWaterSportsCategories(categories);
        }
      } catch (error) {
        console.error("스포츠 카테고리 불러오기 실패:", error);
      }
    };
    
    fetchSports();
  }, []);

  const getSelectedRegionLabel = () => {
    if (regions.length === 0) return "전체";
    const selectedRegionInfo = regions.find(r => r.id === selectedRegion) || regions[0];
    return selectedRegionInfo ? selectedRegionInfo.label : "전체";
  };

  const getSelectedRegionDescription = () => {
    if (regions.length === 0) return "전국 전체 지역";
    const selectedRegionInfo = regions.find(r => r.id === selectedRegion) || regions[0];
    return selectedRegionInfo ? selectedRegionInfo.description : "전국 전체 지역";
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
          {loading && (
            <div style={{
              textAlign: "center",
              padding: "20px",
              color: "#666",
              fontSize: "14px"
            }}>
              🔄 지역 데이터 로딩 중...
            </div>
          )}
          {!loading && (
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
                  {regions.map(region => (
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
          )}
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
