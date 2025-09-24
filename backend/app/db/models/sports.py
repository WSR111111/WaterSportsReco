
from sqlalchemy import Column, Integer, String
from app.db.database import DatabaseManager

class Region(DatabaseManager):
    __tablename__ = "sports"

    sport_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    category_code = Column(String(10), nullable=False, unique=True)  # 수상스포츠 code
    sport_name = Column(String(10), nullable=False)  # 수상스포츠 이름