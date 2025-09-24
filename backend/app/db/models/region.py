from sqlalchemy import Column, Integer, String
from app.db.database import DatabaseManager

class Region(DatabaseManager):
    __tablename__ = "region"

    region_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    lDongRegnCd = Column(String(10), nullable=False)        # 법정동 코드
    lDongSignguCd = Column(String(10), nullable=False, unique=True)  # 시군구 코드
    lDongRegnNm = Column(String(100), nullable=False)       # 법정동 이름
    lDongSignguNm = Column(String(100), nullable=False)     # 시군구 이름
