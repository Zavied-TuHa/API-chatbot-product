from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Test connection DB
def test_db_connection():
    # Kiểm tra kết nối DB để xác nhận hệ thống hoạt động đúng
    try:
        with engine.connect() as connection:
            print("Database connection successful!")
            return True
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return False