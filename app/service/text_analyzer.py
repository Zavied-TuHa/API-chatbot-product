from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from langchain_core.language_models import BaseLLM
from app.utils.response_utils import build_chat_response
import json
from datetime import datetime, UTC
import uuid
from langchain_core.outputs import LLMResult

class TextAnalyzer:
    def __init__(self, llm: BaseLLM):
        self.llm = llm

        # Prompt phân tích văn bản
        self.analysis_prompt = PromptTemplate(
            input_variables=["text"],
            template="""
                        Phân tích văn bản sau và trả về JSON bằng tiếng Việt:
                        Văn bản: {text}
                        Trả về:
                        - semantics: {{ "overall": "ý nghĩa tổng thể", "details": ["ý nghĩa từng câu"] }}
                        - keywords: danh sách từ khóa sản phẩm/dịch vụ, có thể bao gồm cả tên sản phẩm nếu có. (ví dụ: "điện thoại iPhone", "điện thoại Samsung"), bỏ từ ngữ ngữ cảnh ("tôi", "muốn")
                        - intent: ý định chính (ví dụ: "mua sản phẩm", "xem thông tin")
                    """
        )
        self.analysis_chain = RunnableSequence(self.analysis_prompt | self.llm)

        # Prompt phân loại query
        self.classify_prompt = PromptTemplate(
            input_variables=["text"],
            template="""
                        Phân loại văn bản sau thành "specific" (truy vấn rõ ràng) hoặc "ambiguous" (truy vấn mơ hồ).
                        Truy vấn rõ ràng: có đủ thông tin cụ thể (ví dụ: "Tôi muốn mua iPhone 15 Pro Max màu xanh, 256GB").
                        Truy vấn mơ hồ: thiếu thông tin hoặc không rõ (ví dụ: "Có điện thoại nào tốt không?").
                        Văn bản: {text}
                        Trả về: {{ "query_type": "specific" | "ambiguous" }}
                    """
        )
        self.classify_chain = RunnableSequence(self.classify_prompt | self.llm)

        # Prompt làm rõ query mơ hồ
        self.clarify_prompt = PromptTemplate(
            input_variables=["text"],
            template="""
                        Dựa trên truy vấn mơ hồ sau, tạo câu hỏi làm rõ bằng tiếng Việt, tự nhiên, thân thiện:
                        Truy vấn: {text}
                        Trả về: {{ "clarification_question": "câu hỏi" }}
                    """
        )
        self.clarify_chain = RunnableSequence(self.clarify_prompt | self.llm)

    async def classify_query(self, text: str) -> str:
        """Phân loại truy vấn thành specific hoặc ambiguous, trả về lỗi nếu phân tích thất bại"""
        try:
            response = await self.classify_chain.ainvoke({"text": text})

            if isinstance(response, LLMResult):
                return json.loads(response.generations[0][0].text)["query_type"]
            elif isinstance(response, str):
                return json.loads(response)["query_type"]
            else:
                return "error: Định dạng phản hồi không hợp lệ"

        except (json.JSONDecodeError, Exception) as e:
            return f"error: {str(e)}"  # Trả về chuỗi lỗi để endpoint xử lý tiếp

    async def analyze(self, text: str) -> dict:
        """Phân tích truy vấn rõ ràng, trả về JSON chuẩn hóa với từ khóa và ý định"""
        session_id = str(uuid.uuid4())
        timestamp = datetime.now(UTC).isoformat() + "Z"
        try:
            response = await self.analysis_chain.ainvoke({"text": text})

            if isinstance(response, LLMResult):
                result = json.loads(response.generations[0][0].text)
            elif isinstance(response, str):
                result = json.loads(response)
            else:
                raise ValueError("Định dạng phản hồi không hợp lệ")

            messages = [{
                "message_id": f"msg_{uuid.uuid4().hex[:8]}",
                "timestamp": timestamp,
                "sender": "chatbot",
                "text": f"Phân tích: {result['semantics']['overall']}",
                "attachments": []
            }]
            context = {
                "conversation_state": "active",
                "intent": "specific_query",
                "entities": {
                    "keywords": result.get("keywords", []),
                    "intent": result.get("intent", "unknown"),
                    "date": timestamp
                }
            }
            return build_chat_response(session_id, messages, context).model_dump()
        except (json.JSONDecodeError, Exception) as e:
            # Xử lý lỗi JSON hoặc ngoại lệ khác, trả về phản hồi lỗi chuẩn hóa
            messages = [{
                "message_id": f"msg_{uuid.uuid4().hex[:8]}",
                "timestamp": timestamp,
                "sender": "chatbot",
                "text": f"Lỗi: {str(e)}",
                "attachments": []
            }]
            context = {
                "conversation_state": "error",
                "intent": "specific_query",
                "entities": {
                    "keywords": [],
                    "intent": "error",
                    "error_detail": str(e),
                    "date": timestamp
                }
            }
            return build_chat_response(session_id, messages, context).model_dump()

    async def clarify_ambiguous_query(self, text: str) -> dict:
        """Tạo câu hỏi làm rõ cho truy vấn mơ hồ, trả về JSON chuẩn hóa"""
        session_id = str(uuid.uuid4())
        timestamp = datetime.now(UTC).isoformat() + "Z"
        try:
            response = await self.clarify_chain.ainvoke({"text": text})

            if isinstance(response, LLMResult):
                result = json.loads(response.generations[0][0].text)
            elif isinstance(response, str):
                result = json.loads(response)
            else:
                raise ValueError("Định dạng phản hồi không hợp lệ")

            messages = [{
                "message_id": f"msg_{uuid.uuid4().hex[:8]}",
                "timestamp": timestamp,
                "sender": "chatbot",
                "text": result["clarification_question"],
                "attachments": []
            }]
            context = {
                "conversation_state": "clarification_needed",
                "intent": "ambiguous_query",
                "entities": {
                    "original_query": text,
                    "date": timestamp
                }
            }
            return build_chat_response(session_id, messages, context).model_dump()
        except (json.JSONDecodeError, Exception) as e:
            # Xử lý lỗi khi không tạo được câu hỏi làm rõ
            messages = [{
                "message_id": f"msg_{uuid.uuid4().hex[:8]}",
                "timestamp": timestamp,
                "sender": "chatbot",
                "text": f"Lỗi: {str(e)}. Vui lòng cung cấp thêm thông tin.",
                "attachments": []
            }]
            context = {
                "conversation_state": "error",
                "intent": "ambiguous_query",
                "entities": {
                    "original_query": text,
                    "error_detail": str(e),
                    "date": timestamp
                }
            }
            return build_chat_response(session_id, messages, context).model_dump()