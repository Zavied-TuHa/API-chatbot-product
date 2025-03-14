import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import json
from app.service.text_analyzer import TextAnalyzer
from app.service.chatbot_service import chatbot_service


@pytest.mark.asyncio
async def test_classify_query_specific():
    """Kiểm tra phân loại truy vấn rõ ràng"""
    analyzer = TextAnalyzer(llm=chatbot_service.llm)
    result = await analyzer.classify_query("Tôi muốn mua iPhone 15 Pro Max")
    assert result == "specific", "Phải phân loại là specific"


@pytest.mark.asyncio
async def test_classify_query_ambiguous():
    """Kiểm tra phân loại truy vấn mơ hồ"""
    analyzer = TextAnalyzer(llm=chatbot_service.llm)
    result = await analyzer.classify_query("Có điện thoại nào tốt không?")
    assert result == "ambiguous", "Phải phân loại là ambiguous"


@pytest.mark.asyncio
async def test_analyze_specific_query():
    """Kiểm tra phân tích truy vấn rõ ràng"""
    analyzer = TextAnalyzer(llm=chatbot_service.llm)
    result = await analyzer.analyze("Tôi muốn mua iPhone 15 Pro Max")

    assert "session_id" in result, "Phải có session_id"
    assert len(result["messages"]) == 1, "Phải có 1 tin nhắn"
    assert "Phân tích" in result["messages"][0]["text"], "Phải chứa kết quả phân tích"
    assert "keywords" in result["context"]["entities"], "Phải có từ khóa"
    assert result["context"]["conversation_state"] == "active", "Trạng thái phải là active"


@pytest.mark.asyncio
async def test_clarify_ambiguous_query():
    """Kiểm tra làm rõ truy vấn mơ hồ"""
    analyzer = TextAnalyzer(llm=chatbot_service.llm)
    result = await analyzer.clarify_ambiguous_query("Có điện thoại nào tốt không?")

    assert "session_id" in result, "Phải có session_id"
    assert len(result["messages"]) == 1, "Phải có 1 tin nhắn"
    assert "?" in result["messages"][0]["text"], "Phải là câu hỏi làm rõ"
    assert result["context"]["conversation_state"] == "clarification_needed", "Trạng thái phải là clarification_needed"