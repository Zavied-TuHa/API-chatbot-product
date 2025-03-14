import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_analyzer_specific_query():
    """Kiểm tra endpoint /analyzer/analyze với truy vấn rõ ràng"""
    response = client.post("/api/v1/analyzer/analyze", json={"query": "Tôi muốn mua iPhone 15"})
    assert response.status_code == 200, "Phải trả về 200 OK"

    result = response.json()
    assert "session_id" in result, "Phải có session_id"
    assert len(result["messages"]) == 1, "Phải có 1 tin nhắn"
    assert "Phân tích" in result["messages"][0]["text"], "Phải chứa kết quả phân tích"
    assert "keywords" in result["context"]["entities"], "Phải có từ khóa"
    assert result["context"]["conversation_state"] == "active", "Trạng thái phải là active"


def test_analyzer_ambiguous_query():
    """Kiểm tra endpoint /analyzer/analyze với truy vấn mơ hồ"""
    response = client.post("/api/v1/analyzer/analyze", json={"query": "Có điện thoại nào tốt không?"})
    assert response.status_code == 200, "Phải trả về 200 OK"

    result = response.json()
    assert "session_id" in result, "Phải có session_id"
    assert "?" in result["messages"][0]["text"], "Phải là câu hỏi làm rõ"
    assert result["context"]["conversation_state"] == "clarification_needed", "Trạng thái phải là clarification_needed"