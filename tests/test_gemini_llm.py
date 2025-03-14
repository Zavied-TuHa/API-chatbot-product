import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import json
from app.service.Gemini_LLM import GeminiLLM
from app.core.config import settings
from langchain_core.outputs import LLMResult


@pytest.mark.asyncio
async def test_gemini_llm_generate():
    """Kiểm tra khả năng sinh nội dung bất đồng bộ của GeminiLLM"""
    llm = GeminiLLM(api_key=settings.GOOGLE_API_KEY)
    prompts = ["Xin chào, bạn là ai?"]

    result = await llm._agenerate(prompts)

    assert isinstance(result, LLMResult), "Phải trả về LLMResult"
    assert len(result.generations) == 1, "Phải có 1 generation"
    assert len(result.generations[0]) == 1, "Phải có 1 kết quả trong generation"
    assert isinstance(result.generations[0][0].text, str), "Kết quả phải là chuỗi"
    try:
        json.loads(result.generations[0][0].text)  # Kiểm tra định dạng JSON
    except json.JSONDecodeError:
        pytest.fail("Kết quả không phải JSON hợp lệ")


@pytest.mark.asyncio
async def test_gemini_llm_error_handling():
    """Kiểm tra xử lý lỗi khi API thất bại"""
    llm = GeminiLLM(api_key="invalid_key")
    prompts = ["Xin chào"]

    result = await llm._agenerate(prompts)

    assert isinstance(result, LLMResult), "Phải trả về LLMResult ngay cả khi lỗi"
    assert "error" in result.generations[0][0].text, "Phải chứa thông tin lỗi"


def test_gemini_llm_sync_not_implemented():
    """Kiểm tra phương thức đồng bộ ném lỗi"""
    llm = GeminiLLM(api_key=settings.GOOGLE_API_KEY)
    with pytest.raises(NotImplementedError):
        llm._generate(["Xin chào"])