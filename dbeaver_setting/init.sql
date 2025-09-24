-- 지역 관리 테이블
CREATE TABLE region (
    region_id INT AUTO_INCREMENT PRIMARY KEY,
    lDongRegnCd VARCHAR(10) NOT NULL,
    lDongSignguCd VARCHAR(10) NOT NULL UNIQUE,
    lDongRegnNm VARCHAR(100) NOT NULL,
    lDongSignguNm VARCHAR(100) NOT NULL
);

-- 관측소 정보
CREATE TABLE station (
    station_id VARCHAR(20) PRIMARY KEY,
    station_nm VARCHAR(100) NOT NULL,
    lat DECIMAL(9,6) NOT NULL,
    lon DECIMAL(9,6) NOT NULL,
    category VARCHAR(20) NOT NULL  -- MARINE / SURFACE
);

-- 관측 지표 코드
CREATE TABLE observation_code (
    observation_cd VARCHAR(20) PRIMARY KEY,
    observation_nm VARCHAR(100) NOT NULL
);

INSERT INTO observation_code (observation_cd, observation_nm) VALUES
('WS', '풍속'),
('WD', '풍향'),
('TA', '기온'),
('RN', '강수량'),
('WH_SIG', '유의파고'),
('WP', '파주기'),
('TW', '수온');


-- 관측값
CREATE TABLE observation_data (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    station_id VARCHAR(20) NOT NULL,
    observation_cd VARCHAR(20) NOT NULL,
    observation_value DECIMAL(10,3),
    observed_at DATETIME NOT NULL,
    FOREIGN KEY (station_id) REFERENCES station(station_id),
    FOREIGN KEY (observation_cd) REFERENCES observation_code(observation_cd)
);

-- 스포츠 코드 테이블
CREATE TABLE sports (
    sport_id INT AUTO_INCREMENT PRIMARY KEY,
    category_code VARCHAR(10) UNIQUE,
    sport_name VARCHAR(100) NOT NULL COMMENT '스포츠명'
);

-- 수상스포츠 사업장
CREATE TABLE leisure_place (
    leisure_id INT AUTO_INCREMENT PRIMARY KEY,
    category_code VARCHAR(10) NOT NULL,
    content_id VARCHAR(20) UNIQUE,
    place_name VARCHAR(200) NOT NULL,
    address VARCHAR(300),
    address2 VARCHAR(500),
    phone_number VARCHAR(50),
    latitude DECIMAL(10,6),
    longitude DECIMAL(10,6),
    lDongRegnCd VARCHAR(10) NOT NULL,
    lDongSignguCd VARCHAR(10) NOT NULL,
    first_image VARCHAR(500),
    first_image2 VARCHAR(500),
    FOREIGN KEY (lDongSignguCd) REFERENCES region(lDongSignguCd),
    FOREIGN KEY (category_code) REFERENCES sports(category_code)
);

-- 사업장 상세 정보
CREATE TABLE place_detail (
    detail_id INT AUTO_INCREMENT PRIMARY KEY,
    content_id VARCHAR(20) NOT NULL COMMENT '콘텐츠 ID (한국관광공사)',
    homepage TEXT COMMENT '홈페이지 URL',
    overview TEXT COMMENT '개요/상세설명',
    FOREIGN KEY (content_id) REFERENCES leisure_place(content_id)
);

SELECT * FROM region;
SELECT * FROM station;
SELECT * FROM observation_data;
SELECT * FROM sports;
SELECT * FROM leisure_place;
SELECT * FROM place_detail;
