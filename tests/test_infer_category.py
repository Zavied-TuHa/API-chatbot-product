import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import json
from app.service.infer_category import CategoryInferencer
from app.service.chatbot_service import chatbot_service


@pytest.mark.asyncio
async def test_infer_category_valid_keywords():
    """Kiểm tra suy luận danh mục với từ khóa hợp lệ"""
    inferencer = CategoryInferencer(llm=chatbot_service.llm)
    result = await inferencer.infer_category(["iPhone", "điện thoại"])

    assert "session_id" in result, "Phải có session_id"
    assert len(result["messages"]) == 1, "Phải có 1 tin nhắn"
    assert "Danh mục suy luận" in result["messages"][0]["text"], "Phải chứa danh mục"
    assert "category" in result["context"]["entities"], "Phải có danh mục trong entities"
    assert result["context"]["conversation_state"] == "active", "Trạng thái phải là active"


@pytest.mark.asyncio
async def test_infer_category_empty_keywords():
    """Kiểm tra suy luận với từ khóa rỗng"""
    inferencer = CategoryInferencer(llm=chatbot_service.llm)
    result = await inferencer.infer_category([])

    assert "session_id" in result, "Phải có session_id"
    assert "Không suy luận được danh mục" in result["messages"][0]["text"], "Phải báo lỗi từ khóa rỗng"
    assert result["context"]["conversation_state"] == "error", "Trạng thái phải là error"