from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.endpoints import category, analyzer, chatbot
from app.db.session import test_db_connection
import os

app = FastAPI(title="API-Chatbot-Product")

# LangChain tracing để theo dõi hiệu suất
if settings.LANGCHAIN_TRACING_V2 and settings.LANGCHAIN_API_KEY:
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = settings.LANGCHAIN_API_KEY

# Include chatbot endpoints
# Gắn các router với tiền tố /api/v1
app.include_router(analyzer.router, prefix=settings.API_V1_STR)
app.include_router(category.router, prefix=settings.API_V1_STR)
app.include_router(chatbot.router, prefix=settings.API_V1_STR)

@app.get("/")
def health_check():
    return {"message": "Chatbot API is running!"}

@app.get("/tests-db")
def test_database():
    # Kiểm tra kết nối DB để xác nhận hệ thống hoạt động
    if test_db_connection():
        return {"message": "Database connection successful"}
    return {"message": "Database connection failed"}