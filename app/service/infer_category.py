from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from langchain_core.language_models import BaseLLM
from app.utils.response_utils import build_chat_response
import json
from datetime import datetime, UTC
import uuid
from langchain_core.outputs import LLMResult

class CategoryInferencer:
    def __init__(self, llm: BaseLLM):
        self.llm = llm

        # Prompt để suy luận danh mục sản phẩm từ các từ khoá tìm được
        self.category_prompt = PromptTemplate(
            input_variables=["keywords"],
            template="""
                        Dựa trên từ khóa sau, suy luận danh mục sản phẩm bằng tiếng Việt:
                        Từ khóa: {keywords}
                        Trả về: {{ "category": "danh mục" }} (nếu không rõ ràng, trả về {{ "category": null }})
                    """
        )
        self.chain = RunnableSequence(self.category_prompt | self.llm)

    async def infer_category(self, keywords: list) -> dict:
        """Suy luận danh mục từ từ khóa, trả về JSON chuẩn hóa"""
        session_id = str(uuid.uuid4())
        timestamp = datetime.now(UTC).isoformat() + "Z"
        if not keywords:
            # Xử lý trường hợp từ khóa rỗng
            messages = [{
                "message_id": f"msg_{uuid.uuid4().hex[:8]}",
                "timestamp": timestamp,
                "sender": "chatbot",
                "text": "Không suy luận được danh mục",
                "attachments": []
            }]
            context = {
                "conversation_state": "error",
                "intent": "category_inference",
                "entities": {
                    "keywords": keywords,
                    "category": None,
                    "date": timestamp
                }
            }
            return build_chat_response(session_id, messages, context).model_dump()
        try:
            response = await self.chain.ainvoke({"keywords": ", ".join(keywords)})

            if isinstance(response, LLMResult):
                result = json.loads(response.generations[0][0].text)
            elif isinstance(response, str):
                result = json.loads(response)
            else:
                raise ValueError("Định dạng phản hồi không hợp lệ")

            category = result.get("category") if isinstance(result, dict) else None
            messages = [{
                "message_id": f"msg_{uuid.uuid4().hex[:8]}",
                "timestamp": timestamp,
                "sender": "chatbot",
                "text": f"Danh mục suy luận: {category}" if category else "Không suy luận được danh mục",
                "attachments": []
            }]
            context = {
                "conversation_state": "active" if category else "error",
                "intent": "category_inference",
                "entities": {
                    "keywords": keywords,
                    "category": category,
                    "date": timestamp
                }
            }
            return build_chat_response(session_id, messages, context).model_dump()
        except (json.JSONDecodeError, Exception) as e:
            # Xử lý lỗi khi LLM trả về dữ liệu không hợp lệ
            messages = [{
                "message_id": f"msg_{uuid.uuid4().hex[:8]}",
                "timestamp": timestamp,
                "sender": "chatbot",
                "text": f"Lỗi: {str(e)}",
                "attachments": []
            }]
            context = {
                "conversation_state": "error",
                "intent": "category_inference",
                "entities": {
                    "keywords": keywords,
                    "category": None,
                    "error_detail": str(e),
                    "date": timestamp
                }
            }
            return build_chat_response(session_id, messages, context).model_dump()