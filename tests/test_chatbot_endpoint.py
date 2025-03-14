import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_chat_endpoint():
    """Kiểm tra endpoint /chatbot/chat"""
    response = client.post("/api/v1/chatbot/chat", json={"query": "Xin chào"})
    assert response.status_code == 200, "Phải trả về 200 OK"

    result = response.json()
    assert "session_id" in result, "Phải có session_id"
    assert len(result["messages"]) == 1, "Phải có 1 tin nhắn"
    assert result["messages"][0]["sender"] == "chatbot", "Người gửi phải là chatbot"
    assert result["context"]["conversation_state"] == "active", "Trạng thái phải là active"


def test_history_endpoint_empty():
    """Kiểm tra endpoint /chatbot/history với session rỗng"""
    session_id = "test_empty_session"
    response = client.post("/api/v1/chatbot/history", json={"session_id": session_id})
    assert response.status_code == 200, "Phải trả về 200 OK"

    result = response.json()
    assert result["session_id"] == session_id, "session_id phải khớp"
    assert len(result["messages"]) == 0, "Không có tin nhắn khi lịch sử rỗng"
    assert result["context"]["conversation_state"] == "inactive", "Trạng thái phải là inactive"


def test_history_endpoint_with_messages():
    """Kiểm tra endpoint /chatbot/history với lịch sử"""
    session_id = "test_history_session"
    client.post("/api/v1/chatbot/chat", json={"query": "Xin chào", "session_id": session_id})
    response = client.post("/api/v1/chatbot/history", json={"session_id": session_id, "limit": 1})
    assert response.status_code == 200, "Phải trả về 200 OK"

    result = response.json()
    print(f"Response JSON: {result}")
    assert len(result["messages"]) == 2, "Phải có 2 tin nhắn (user + chatbot)"
    assert result["context"]["entities"]["retrieved_count"] == 1, "Số tin nhắn lấy ra phải là 1"  # Sửa thành entities