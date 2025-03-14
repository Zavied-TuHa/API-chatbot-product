import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import json
from app.service.chatbot_service import ChatbotService, chatbot_service


@pytest.mark.asyncio
async def test_process_chat():
    """Kiểm tra xử lý truy vấn trò chuyện"""
    session_id = "test_session_1"
    query = "Xin chào"
    result = await chatbot_service.process_chat(query, session_id)

    assert "session_id" in result, "Phải có session_id"
    assert result["session_id"] == session_id, "session_id phải khớp"
    assert len(result["messages"]) == 1, "Phải có 1 tin nhắn"
    assert result["messages"][0]["sender"] == "chatbot", "Người gửi phải là chatbot"
    assert "text" in result["messages"][0], "Phải có nội dung phản hồi"
    assert result["context"]["conversation_state"] == "active", "Trạng thái phải là active"


@pytest.mark.asyncio
async def test_retrieve_chat_history_empty():
    """Kiểm tra truy xuất lịch sử khi chưa có"""
    session_id = "test_session_empty"
    result = await chatbot_service.retrieve_chat_history(session_id)

    assert result["session_id"] == session_id, "session_id phải khớp"
    assert len(result["messages"]) == 0, "Không có tin nhắn khi lịch sử rỗng"
    assert result["context"]["conversation_state"] == "inactive", "Trạng thái phải là inactive"


@pytest.mark.asyncio
async def test_retrieve_chat_history_with_messages():
    """Kiểm tra truy xuất lịch sử với tin nhắn"""
    session_id = "test_session_history"
    await chatbot_service.process_chat("Xin chào", session_id)
    await chatbot_service.process_chat("Bạn khỏe không?", session_id)

    result = await chatbot_service.retrieve_chat_history(session_id, limit=1)

    assert len(result["messages"]) == 2, "Phải có 2 tin nhắn (1 cặp user + chatbot)"
    assert result["context"]["entities"]["retrieved_count"] == 1, "Số tin nhắn lấy ra phải khớp với limit"  # Sửa thành entities