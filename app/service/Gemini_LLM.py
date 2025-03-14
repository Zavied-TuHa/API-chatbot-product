import google.generativeai as genai
from typing import List, Optional, Any
from langchain_core.language_models import BaseLLM
from langchain_core.callbacks import AsyncCallbackManagerForLLMRun
from langchain_core.outputs import LLMResult, Generation
import json
import asyncio

class GeminiLLM(BaseLLM):
    """Custom LLM wrapper cho Google Gemini"""
    api_key: str
    max_retries: int = 3  # Số lần thử lại khi gọi API thất bại

    def __init__(self, api_key: str, max_retries: int = 3):
        """Khởi tạo Gemini LLM với API key và số lần thử lại"""
        super().__init__(api_key=api_key)
        self.max_retries = max_retries

    async def _agenerate(
            self,
            prompts: List[str],
            stop: Optional[List[str]] = None,
            run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
            **kwargs: Any
    ) -> LLMResult:
        """Gọi Gemini API bất đồng bộ, trả về kết quả theo định dạng LangChain"""
        genai.configure(api_key=self.api_key)
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            generation_config={
                "temperature": kwargs.get("temperature", 0.7),  # Linh hoạt temperature qua kwargs
                "response_mime_type": "application/json"
            }
        )
        last_error = None
        for attempt in range(self.max_retries):
            try:
                response = await model.generate_content_async(prompts[0])
                return LLMResult(generations=[[Generation(text=response.text)]])
            except Exception as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(1)  # Chờ 1 giây trước khi thử lại
                    continue
        # Nếu hết số lần thử, trả về thông báo lỗi
        error_json = json.dumps({"error": str(last_error)})
        return LLMResult(generations=[[Generation(text=error_json)]])

    def _generate(self, *args, **kwargs):
        """Phương thức đồng bộ không hỗ trợ, buộc dùng async"""
        raise NotImplementedError("Use async version with agenerate")

    @property
    def _llm_type(self):
        """Xác định loại LLM cho LangChain"""
        return "gemini"