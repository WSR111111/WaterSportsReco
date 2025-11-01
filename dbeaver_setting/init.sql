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
('obs', 'root', '지표 루트', NULL)
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



