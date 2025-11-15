-- 포스트그리

-- 코드 테이블
CREATE TABLE code (
    code VARCHAR(50) PRIMARY KEY,            -- 코드 값 (ex. reg01, obs_ocean)
    code_desc VARCHAR(100) NOT NULL,         -- 코드 설명 (테이블 내부 식별용)
    code_name VARCHAR(100) NOT NULL,         -- 코드명 (표시용)
    upper_code VARCHAR(50),                  -- 상위 코드
    CONSTRAINT fk_upper_code
        FOREIGN KEY (upper_code)
        REFERENCES code(code)
        ON UPDATE CASCADE
        ON DELETE SET NULL
);

-- 코드테이블에 지표 INSERT
-- 최상위 그룹
INSERT INTO code (code, code_desc, code_name, upper_code)
VALUES
('reg', 'root', '지역코드 루트', NULL),
('cat', 'root', '스포츠카테고리 루트', NULL),
('obs', 'root', '지표 루트', NULL),
('forecast', 'root', '예보 루트', NULL)
ON CONFLICT (code) DO NOTHING;

-- 해양지표 그룹
INSERT INTO code (code, code_desc, code_name, upper_code)
VALUES 
('obs_ocean', 'obs_cd', '해양지표', 'obs'), 
('obs_ocean_TA', 'obs_cd', '기온(해수면 근처 공기 온도)', 'obs_ocean'),
('obs_ocean_TW', 'obs_cd', '수온(해수면 온도)', 'obs_ocean'), 
('obs_ocean_WD', 'obs_cd', '풍향(바람이 불어오는 방향)', 'obs_ocean'),
('obs_ocean_WS', 'obs_cd', '풍속(바람의 속도)', 'obs_ocean'),
('obs_ocean_WH', 'obs_cd', '유의파고(파도의 평균 높이)', 'obs_ocean'),
('obs_ocean_WP', 'obs_cd', '파주기(파도의 주기)', 'obs_ocean');

-- 지상지표 그룹
INSERT INTO code (code, code_desc, code_name, upper_code)
VALUES 
('obs_ground', 'obs_cd', '지상지표', 'obs'),
('obs_ground_TA', 'obs_cd', '기온(대기 온도)', 'obs_ground'),
('obs_ground_WD', 'obs_cd', '풍향(바람이 불어오는 방향)', 'obs_ground'),
('obs_ground_WS', 'obs_cd', '풍속(바람의 속도)', 'obs_ground'),
('obs_ground_RN', 'obs_cd', '강수량(비의 양)', 'obs_ground');

-- 육상 예보 (ground)
INSERT INTO code (code, code_desc, code_name, upper_code)
VALUES
('forecast_ground', 'forecast_cd', '육상 예보', 'forecast'),
('forecast_ground_W1', 'forecast_cd', '예보 시작지점 풍향', 'forecast_ground'),
('forecast_ground_W2', 'forecast_cd', '예보 종료지점 풍향', 'forecast_ground'),
('forecast_ground_TA', 'forecast_cd', '기온', 'forecast_ground'),
('forecast_ground_ST', 'forecast_cd', '강수확률', 'forecast_ground'),
('forecast_ground_SKY', 'forecast_cd', '하늘상태코드', 'forecast_ground'),
('forecast_ground_PREP', 'forecast_cd', '강수유무코드', 'forecast_ground'),
('forecast_ground_WF', 'forecast_cd', '예보 텍스트', 'forecast_ground')
ON CONFLICT (code) DO NOTHING;

-- 해상 예보 (ocean)
INSERT INTO code (code, code_desc, code_name, upper_code)
VALUES
('forecast_ocean', 'forecast_cd', '해상 예보', 'forecast'),
('forecast_ocean_W1', 'forecast_cd', '예보 시작지점 풍향', 'forecast_ocean'),
('forecast_ocean_W2', 'forecast_cd', '예보 종료지점 풍향', 'forecast_ocean'),
('forecast_ocean_S1', 'forecast_cd', '풍속(시작값)', 'forecast_ocean'),
('forecast_ocean_S2', 'forecast_cd', '풍속(종료값)', 'forecast_ocean'),
('forecast_ocean_WH1', 'forecast_cd', '파고(시작값)', 'forecast_ocean'),
('forecast_ocean_WH2', 'forecast_cd', '파고(종료값)', 'forecast_ocean'),
('forecast_ocean_PREP', 'forecast_cd', '강수유무코드', 'forecast_ocean'),
('forecast_ocean_SKY', 'forecast_cd', '하늘상태코드', 'forecast_ocean'),
('forecast_ocean_WF', 'forecast_cd', '예보 텍스트', 'forecast_ocean')
ON CONFLICT (code) DO NOTHING;


-- 관측소 테이블
CREATE TABLE observation_station (
    station_id   VARCHAR(20) PRIMARY KEY,       -- 관측소 ID (예: 100, 101 등)
    station_nm   VARCHAR(100) NOT NULL,         -- 관측소 이름 (예: 대관령, 백령도)
    lat          NUMERIC(9,6) NOT NULL,         -- 위도
    lon          NUMERIC(9,6) NOT NULL,         -- 경도
    obs_cd       VARCHAR(50) NOT NULL,          -- 코드테이블(code.code) 참조 (ex. obs_ground, obs_ocean)
    created_at   TIMESTAMP DEFAULT NOW(),       -- 생성일시
    updated_at   TIMESTAMP DEFAULT NOW(),       -- 수정일시
    CONSTRAINT fk_observation_station_obs_cd
        FOREIGN KEY (obs_cd)
        REFERENCES code(code)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

-- 관측값 테이블
CREATE TABLE observation_data (
    id SERIAL PRIMARY KEY,                           -- 고유 식별자
    station_id VARCHAR(20) NOT NULL,                 -- 관측소 ID (FK)
    obs_cd VARCHAR(50) NOT NULL,                     -- 관측항목 코드 (FK → code.code)
    observation_value NUMERIC(10,3) NOT NULL,        -- 관측값
    observed_at TIMESTAMP NOT NULL,                  -- 관측 시각

    CONSTRAINT fk_observation_station
        FOREIGN KEY (station_id)
        REFERENCES observation_station(station_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_observation_cd
        FOREIGN KEY (obs_cd)
        REFERENCES code(code)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

ALTER TABLE observation_data ADD CONSTRAINT unique_observation 
UNIQUE (station_id, obs_cd, observed_at);

-- ------------------------------------------------------------------------------------
-- 단기 예보 관측소 및 관측값 테이블
-- ------------------------------------------------------------------------------------
CREATE TABLE short_term_station (
    station_id VARCHAR(10) PRIMARY KEY,         -- 예보구역코드 (REG_ID)
    reg_sp CHAR(3),                         -- 구역특성 (A~P)
    reg_name VARCHAR(100),                  -- 예보구역명 (REG_NAME)
    created_at TIMESTAMP DEFAULT NOW()
);

-- 단기 예보 관측값 테이블
CREATE TABLE observation_data_short (
    id SERIAL PRIMARY KEY,
    station_id VARCHAR(10) NOT NULL,          -- 예보구역코드
    obs_code VARCHAR(50) NOT NULL,            -- 관측항목 코드 (code 테이블 참조)
    obs_value VARCHAR(100),                   -- 예보값 (WF가 텍스트인 경우도 있음)
    tm_fc TIMESTAMP NOT NULL,                 -- 발표시각
    tm_ef TIMESTAMP NOT NULL,                 -- 발효시각
    created_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT fk_obs_code_short
        FOREIGN KEY (obs_code) REFERENCES code (code)
        ON DELETE RESTRICT,
    CONSTRAINT fk_station_short
        FOREIGN KEY (station_id) REFERENCES short_term_station (station_id)
        ON DELETE CASCADE
);
-- ------------------------------------------------------------------------------------
-- 중기 예보 관측소 및 관측값 테이블
-- ------------------------------------------------------------------------------------
CREATE TABLE medium_term_station (
    reg_id VARCHAR(10) PRIMARY KEY,         -- 예보구역코드 (REG_ID)
    reg_sp CHAR(3),                         -- 구역특성 (A:육상, C:도시, H:해상)
    reg_name VARCHAR(100),                  -- 예보구역명 (REG_NAME)
    created_at TIMESTAMP DEFAULT NOW()
);

-- 중기 예보 관측값 테이블
CREATE TABLE observation_data_medium (
    id SERIAL PRIMARY KEY,
    station_id VARCHAR(10) NOT NULL,          -- 예보구역코드
    obs_code VARCHAR(50) NOT NULL,            -- 관측항목 코드 (code 테이블 참조)
    obs_value VARCHAR(100),
    tm_fc TIMESTAMP NOT NULL,                 -- 발표시각
    tm_ef TIMESTAMP,                          -- 발효시각(없을 수도 있음)
    created_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT fk_obs_code_medium
        FOREIGN KEY (obs_code) REFERENCES code (code)
        ON DELETE RESTRICT,
    CONSTRAINT fk_station_medium
        FOREIGN KEY (station_id) REFERENCES medium_term_station (reg_id)
        ON DELETE CASCADE
);



-- 수상 스포츠 사업장 테이블
CREATE TABLE leisure_place (
    leisure_id      SERIAL PRIMARY KEY,          -- 고유 식별자
    cat_cd          VARCHAR(50),                 -- NOT NULL 제거!
    content_id      BIGINT UNIQUE NOT NULL,      -- TourAPI 등 외부 API의 콘텐츠 ID
    place_name      VARCHAR(200) NOT NULL,       -- 장소명
    address         VARCHAR(300),                -- 기본 주소
    address2        VARCHAR(300),                -- 상세 주소
    phone_number    VARCHAR(50),                 -- 전화번호
    latitude        NUMERIC(10,6),               -- 위도
    longitude       NUMERIC(10,6),               -- 경도
    reg_cd          VARCHAR(50),                 -- 지역 코드
    first_image     TEXT,                        -- 대표 이미지 URL 1
    first_image2    TEXT,                        -- 대표 이미지 URL 2
    
    CONSTRAINT fk_leisure_category
        FOREIGN KEY (cat_cd)
        REFERENCES code(code)
        ON UPDATE CASCADE
        ON DELETE SET NULL,                      -- 변경!
        
    CONSTRAINT fk_leisure_region
        FOREIGN KEY (reg_cd)
        REFERENCES code(code)
        ON UPDATE CASCADE
        ON DELETE SET NULL
);


-- 수상 스포츠 사업장 상세 정보 테이블
CREATE TABLE leisure_place_detail (
    detail_id   SERIAL PRIMARY KEY,              -- 고유 식별자
    content_id  BIGINT UNIQUE NOT NULL,          -- 관련 콘텐츠 ID (FK → leisure_place.content_id)
    homepage    TEXT,                            -- 홈페이지 URL
    overview    TEXT,                            -- 상세 설명
    created_at  TIMESTAMP DEFAULT NOW(),         -- 생성일시
    updated_at  TIMESTAMP DEFAULT NOW(),         -- 수정일시

    CONSTRAINT fk_leisure_place_detail
        FOREIGN KEY (content_id)
        REFERENCES leisure_place(content_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);



