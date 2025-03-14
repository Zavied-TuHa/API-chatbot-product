import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv(override=True)  # Load environment variables from .env file

class Settings(BaseSettings):
    """Cấu hình ứng dụng từ biến môi trường hoặc giá trị mặc định"""
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    LANGCHAIN_TRACING_V2: bool = os.getenv("LANGCHAIN_TRACING_V2", "true").lower() == "true"
    LANGCHAIN_API_KEY: str = os.getenv("LANGCHAIN_API_KEY", "")
    MAX_CHAT_MESSAGES: int = int(os.getenv("MAX_CHAT_MESSAGES", 100))  # Giới hạn tin nhắn trong lịch sử

    # Cấu hình database
    PGHOST: str
    PGDATABASE: str
    PGUSER: str
    PGPASSWORD: str
    PGPORT: str
    PGSSLMODE: str

    # URI kết nối database
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.PGUSER}:{self.PGPASSWORD}@{self.PGHOST}:{self.PGPORT}/{self.PGDATABASE}?sslmode={self.PGSSLMODE}"

    class Config:
        # Đảm bảo cấu hình nhạy cảm với chữ hoa/thường và bỏ qua biến thừa
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()
