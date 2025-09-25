import { useParams, useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';

export default function PlaceDetail() {
    const { placeId } = useParams();
    const navigate = useNavigate();
    const [placeData, setPlaceData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // TODO: API 호출로 장소 상세 정보 가져오기
        // const fetchPlaceDetail = async () => {
        //   try {
        //     const response = await getPlaceDetail(placeId);
        //     setPlaceData(response.data);
        //   } catch (error) {
        //     console.error('장소 상세 정보 로드 실패:', error);
        //   } finally {
        //     setLoading(false);
        //   }
        // };
        // fetchPlaceDetail();

        // 임시 데이터
        setTimeout(() => {
            setPlaceData({
                id: placeId,
                name: '플로우하우스 용인',
                address: '경기도 용인시 처인구 모현읍',
                sport_name: '윈드서핑/제트스키',
                description: '최신 시설을 갖춘 수상스포츠 체험장입니다.',
                phone: '031-123-4567',
                website: 'https://example.com',
                operating_hours: '09:00 - 18:00',
                images: ['/images/yacht.png']
            });
            setLoading(false);
        }, 1000);
    }, [placeId]);

    if (loading) {
        return (
            <div style={{
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                height: '100vh',
                backgroundColor: '#f5f5f5'
            }}>
                <div>로딩 중...</div>
            </div>
        );
    }

    if (!placeData) {
        return (
            <div style={{
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                height: '100vh',
                flexDirection: 'column',
                backgroundColor: '#f5f5f5'
            }}>
                <h2>장소를 찾을 수 없습니다</h2>
                <button
                    onClick={() => navigate('/')}
                    style={{
                        padding: '10px 20px',
                        backgroundColor: '#007bff',
                        color: 'white',
                        border: 'none',
                        borderRadius: '5px',
                        cursor: 'pointer'
                    }}
                >
                    홈으로 돌아가기
                </button>
            </div>
        );
    }

    return (
        <div style={{ minHeight: '100vh', backgroundColor: '#f8f9fa' }}>
            {/* 헤더 */}
            <div style={{
                backgroundColor: 'white',
                padding: '20px',
                borderBottom: '1px solid #dee2e6',
                boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
            }}>
                <button
                    onClick={() => navigate('/')}
                    style={{
                        backgroundColor: '#6c757d',
                        color: 'white',
                        border: 'none',
                        padding: '8px 16px',
                        borderRadius: '5px',
                        cursor: 'pointer',
                        marginBottom: '15px'
                    }}
                >
                    ← 지도로 돌아가기
                </button>

                <h1 style={{ margin: '0 0 10px 0', color: '#333' }}>
                    {placeData.name}
                </h1>

                <p style={{ margin: 0, color: '#007bff', fontSize: '16px' }}>
                    🏄 {placeData.sport_name}
                </p>
            </div>

            {/* 메인 콘텐츠 */}
            <div style={{
                maxWidth: '1200px',
                margin: '0 auto',
                padding: '30px 20px'
            }}>
                <div style={{
                    display: 'grid',
                    gridTemplateColumns: '1fr 1fr',
                    gap: '30px',
                    '@media (max-width: 768px)': {
                        gridTemplateColumns: '1fr'
                    }
                }}>
                    {/* 기본 정보 */}
                    <div style={{
                        backgroundColor: 'white',
                        padding: '25px',
                        borderRadius: '10px',
                        boxShadow: '0 2px 10px rgba(0,0,0,0.1)'
                    }}>
                        <h2 style={{ marginTop: 0, color: '#333' }}>기본 정보</h2>

                        <div style={{ marginBottom: '15px' }}>
                            <strong>📍 주소:</strong>
                            <p style={{ margin: '5px 0', color: '#666' }}>{placeData.address}</p>
                        </div>

                        <div style={{ marginBottom: '15px' }}>
                            <strong>📞 전화번호:</strong>
                            <p style={{ margin: '5px 0', color: '#666' }}>{placeData.phone}</p>
                        </div>

                        <div style={{ marginBottom: '15px' }}>
                            <strong>🕐 운영시간:</strong>
                            <p style={{ margin: '5px 0', color: '#666' }}>{placeData.operating_hours}</p>
                        </div>

                        {placeData.website && (
                            <div style={{ marginBottom: '15px' }}>
                                <strong>🌐 웹사이트:</strong>
                                <p style={{ margin: '5px 0' }}>
                                    <a
                                        href={placeData.website}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        style={{ color: '#007bff', textDecoration: 'none' }}
                                    >
                                        {placeData.website}
                                    </a>
                                </p>
                            </div>
                        )}
                    </div>

                    {/* 상세 설명 */}
                    <div style={{
                        backgroundColor: 'white',
                        padding: '25px',
                        borderRadius: '10px',
                        boxShadow: '0 2px 10px rgba(0,0,0,0.1)'
                    }}>
                        <h2 style={{ marginTop: 0, color: '#333' }}>상세 설명</h2>
                        <p style={{ lineHeight: '1.6', color: '#666' }}>
                            {placeData.description}
                        </p>

                        {/* 이미지 갤러리 */}
                        {placeData.images && placeData.images.length > 0 && (
                            <div style={{ marginTop: '20px' }}>
                                <h3 style={{ color: '#333' }}>사진</h3>
                                <div style={{
                                    display: 'grid',
                                    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                                    gap: '15px',
                                    marginTop: '15px'
                                }}>
                                    {placeData.images.map((image, index) => (
                                        <img
                                            key={index}
                                            src={image}
                                            alt={`${placeData.name} 이미지 ${index + 1}`}
                                            style={{
                                                width: '100%',
                                                height: '150px',
                                                objectFit: 'cover',
                                                borderRadius: '8px',
                                                boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
                                            }}
                                            onError={(e) => e.target.style.display = 'none'}
                                        />
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                </div>

                {/* 추가 정보 섹션 */}
                <div style={{
                    backgroundColor: 'white',
                    padding: '25px',
                    borderRadius: '10px',
                    boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
                    marginTop: '30px'
                }}>
                    <h2 style={{ marginTop: 0, color: '#333' }}>이용 안내</h2>
                    <div style={{
                        display: 'grid',
                        gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
                        gap: '20px'
                    }}>
                        <div>
                            <h4 style={{ color: '#007bff' }}>🏄‍♂️ 체험 프로그램</h4>
                            <p style={{ color: '#666' }}>다양한 수상스포츠 체험 프로그램을 제공합니다.</p>
                        </div>

                        <div>
                            <h4 style={{ color: '#28a745' }}>🎯 예약 안내</h4>
                            <p style={{ color: '#666' }}>사전 예약을 통해 더 나은 서비스를 받으실 수 있습니다.</p>
                        </div>

                        <div>
                            <h4 style={{ color: '#ffc107' }}>⚠️ 주의사항</h4>
                            <p style={{ color: '#666' }}>안전을 위해 안전수칙을 반드시 준수해주세요.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}