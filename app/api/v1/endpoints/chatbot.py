from fastapi import APIRouter
from app.service.chatbot_service import chatbot_service
from app.utils.response_utils import ChatResponse
from app.utils.validation_utils import ChatRequest, HistoryRequest
import uuid

router = APIRouter(prefix="/chatbot", tags=["chatbot"])

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Xử lý truy vấn trò chuyện, trả về phản hồi chuẩn hóa"""
    session_id = request.session_id or str(uuid.uuid4())  # Tạo session_id nếu không có
    result = await chatbot_service.process_chat(request.query, session_id)
    # return result  # Trả thẳng dict
    return ChatResponse(**result)

@router.post("/history", response_model=ChatResponse)
async def get_chat_history(request: HistoryRequest):
    """Truy xuất lịch sử trò chuyện, trả về phản hồi chuẩn hóa"""
    history = await chatbot_service.retrieve_chat_history(request.session_id, request.limit)
    # return history  # Trả thẳng dict
    return ChatResponse(**history)