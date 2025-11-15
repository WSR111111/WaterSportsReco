import { useState, useEffect } from 'react';
import { getPlaceDetail } from '../api/client';
import Header from '../components/Header';
import Footer from '../components/Footer';
import { navigate } from '../router';

export default function PlaceDetail({ placeId }) {
    const [placeData, setPlaceData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchPlaceDetail = async () => {
            console.log('PlaceDetail - placeId:', placeId);

            if (!placeId) {
                console.error('placeId가 없습니다');
                setPlaceData(null);
                setLoading(false);
                return;
            }

            try {
                console.log('API 호출 시작:', placeId);
                const result = await getPlaceDetail(placeId);
                console.log('API 응답 데이터:', result);
                
                if (result.success && result.place) {
                    setPlaceData(result.place);
                    setError(null);
                } else {
                    setError(result.error || '장소 정보를 찾을 수 없습니다');
                    setPlaceData(null);
                }
            } catch (error) {
                console.error('장소 상세 정보 로드 실패:', error);
                setError(error.message || '알 수 없는 오류가 발생했습니다');
                setPlaceData(null);
            } finally {
                setLoading(false);
            }
        };

        fetchPlaceDetail();
    }, [placeId]);

    if (loading) {
        return (
            <div style={{
                display: 'flex',
                flexDirection: 'column',
                minHeight: '100vh',
                backgroundColor: '#f5f5f5'
            }}>
                <Header />
                <div style={{
                    flex: 1,
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center'
                }}>
                    <div>로딩 중...</div>
                </div>
                <Footer />
            </div>
        );
    }

    if (!placeData) {
        return (
            <div style={{
                display: 'flex',
                flexDirection: 'column',
                minHeight: '100vh',
                backgroundColor: '#f5f5f5'
            }}>
                <Header />
                <div style={{
                    flex: 1,
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center',
                    flexDirection: 'column'
                }}>
                    <h2>장소를 찾을 수 없습니다</h2>
                    <p style={{ color: '#666', marginBottom: '20px' }}>
                        요청한 ID: {placeId}
                    </p>
                    {error && (
                        <p style={{ color: '#dc3545', marginBottom: '20px', textAlign: 'center' }}>
                            오류: {error}
                        </p>
                    )}
                    <button
                        onClick={() => navigate.toHome()}
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
                <Footer />
            </div>
        );
    }

    return (
        <div style={{
            display: 'flex',
            flexDirection: 'column',
            minHeight: '100vh',
            backgroundColor: '#f8f9fa'
        }}>
            <Header />

            {/* 장소 정보 헤더 */}
            <div style={{
                backgroundColor: 'white',
                padding: '20px',
                borderBottom: '1px solid #dee2e6',
                boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
            }}>
                <button
                    onClick={() => navigate.toHome()}
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
                    {placeData.place_name}
                </h1>

                <p style={{ margin: 0, color: '#007bff', fontSize: '16px' }}>
                    🏄‍♂️ {placeData.category_name || '레저스포츠 시설'}
                </p>
            </div>

            {/* 메인 콘텐츠 */}
            <div style={{
                flex: 1,
                maxWidth: '1200px',
                margin: '0 auto',
                padding: '30px 20px',
                width: '100%'
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
                            <p style={{ margin: '5px 0', color: '#666' }}>
                                {placeData.address}
                                {placeData.address2 && <><br />{placeData.address2}</>}
                            </p>
                        </div>

                        {placeData.phone_number && (
                            <div style={{ marginBottom: '15px' }}>
                                <strong>📞 전화번호:</strong>
                                <p style={{ margin: '5px 0', color: '#666' }}>{placeData.phone_number}</p>
                            </div>
                        )}

                        <div style={{ marginBottom: '15px' }}>
                            <strong>🏷️ 지역:</strong>
                            <p style={{ margin: '5px 0', color: '#666' }}>
                                {placeData.region_name || '지역 정보 없음'}
                            </p>
                        </div>

                        <div style={{ marginBottom: '15px' }}>
                            <strong>🏄‍♂️ 스포츠 종목:</strong>
                            <p style={{ margin: '5px 0', color: '#666' }}>
                                {placeData.category_name || '레저스포츠 시설'}
                            </p>
                        </div>

                        {placeData.homepage && (
                            <div style={{ marginBottom: '15px' }}>
                                <strong>🌐 웹사이트:</strong>
                                <p style={{ margin: '5px 0' }}>
                                    <a
                                        href={placeData.homepage}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        style={{ color: '#007bff', textDecoration: 'none' }}
                                    >
                                        {placeData.homepage}
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
                            {placeData.overview || '상세 설명이 없습니다.'}
                        </p>

                        {/* 이미지 갤러리 */}
                        {(placeData.first_image || placeData.first_image2) && (
                            <div style={{ marginTop: '20px' }}>
                                <h3 style={{ color: '#333' }}>사진</h3>
                                <div style={{
                                    display: 'grid',
                                    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                                    gap: '15px',
                                    marginTop: '15px'
                                }}>
                                    {placeData.first_image && (
                                        <img
                                            src={placeData.first_image}
                                            alt={`${placeData.place_name} 이미지 1`}
                                            style={{
                                                width: '100%',
                                                height: '150px',
                                                objectFit: 'cover',
                                                borderRadius: '8px',
                                                boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
                                            }}
                                            onError={(e) => e.target.style.display = 'none'}
                                        />
                                    )}
                                    {placeData.first_image2 && (
                                        <img
                                            src={placeData.first_image2}
                                            alt={`${placeData.place_name} 이미지 2`}
                                            style={{
                                                width: '100%',
                                                height: '150px',
                                                objectFit: 'cover',
                                                borderRadius: '8px',
                                                boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
                                            }}
                                            onError={(e) => e.target.style.display = 'none'}
                                        />
                                    )}
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
                            <p style={{ color: '#666' }}>
                                {placeData.category_name ? 
                                    `${placeData.category_name} 체험 프로그램을 제공합니다.` : 
                                    '다양한 레저스포츠 체험 프로그램을 제공합니다.'
                                }
                            </p>
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

            <Footer />
        </div>
    );
}