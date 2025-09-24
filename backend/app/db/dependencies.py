from app.db.database import DatabaseManager

def get_db():
    db = DatabaseManager()
    connection = db.connect()
    try:
        yield db  
    finally:
        db.disconnect()
