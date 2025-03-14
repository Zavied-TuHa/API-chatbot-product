import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_category_infer_valid_keywords():
    """Kiểm tra endpoint /category/infer với từ khóa hợp lệ"""
    response = client.post("/api/v1/category/infer", json={"keywords": ["iPhone", "điện thoại"]})
    assert response.status_code == 200, "Phải trả về 200 OK"

    result = response.json()
    assert "session_id" in result, "Phải có session_id"
    assert "Danh mục suy luận" in result["messages"][0]["text"], "Phải chứa danh mục"
    assert "category" in result["context"]["entities"], "Phải có danh mục trong entities"
    assert result["context"]["conversation_state"] == "active", "Trạng thái phải là active"


def test_category_infer_empty_keywords():
    """Kiểm tra endpoint /category/infer với từ khóa rỗng"""
    response = client.post("/api/v1/category/infer", json={"keywords": []})
    assert response.status_code == 400, "Phải trả về 400 khi từ khóa rỗng"