from app.core.config import settings
from app.service.Gemini_LLM import GeminiLLM
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from app.utils.response_utils import build_chat_response, message_to_dict
from typing import Dict, Optional
import json
from datetime import datetime, UTC
import uuid
from langchain_core.outputs import LLMResult

class ChatbotService:
    def __init__(self):
        self.llm = GeminiLLM(api_key=settings.GOOGLE_API_KEY)
        self.bot_name = "API-chatbot-Product"

        # Lưu trữ lịch sử trò chuyện cho từng session
        self.chat_histories: Dict[str, ChatMessageHistory] = {}

        # Định nghĩa prompt cho chatbot
        self.chat_prompt = ChatPromptTemplate.from_messages([
            ("system", """
                        Bạn là {bot_name}. Nếu câu hỏi là lời chào hỏi (ví dụ: xin chào, hi, good morning), 
                        hãy trả lời lịch sự bằng tiếng Việt, giới thiệu bản thân và hỏi người dùng cần giúp gì.
                        Nếu không, trả lời tự nhiên theo nội dung câu hỏi, không thêm lời chào trừ khi là lần đầu hoặc được yêu cầu.
                        Không tự giới thiệu trừ khi được yêu cầu hoặc đây là lần đầu tiên.
                        Trả về JSON với trường "response" chứa câu trả lời.
                    """.format(bot_name=self.bot_name)),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}")
        ])

        self.chain = self.chat_prompt | self.llm

    def _get_session_history(self, session_id: str) -> ChatMessageHistory:
        """Lấy hoặc tạo lịch sử trò chuyện cho session, giới hạn số tin nhắn"""
        if session_id not in self.chat_histories:
            self.chat_histories[session_id] = ChatMessageHistory()
        history = self.chat_histories[session_id]
        max_messages = settings.MAX_CHAT_MESSAGES
        if len(history.messages) > max_messages:
            history.messages = history.messages[-max_messages:]  # Cắt bớt nếu vượt giới hạn
        return history

    async def process_chat(self, query: str, session_id: str) -> dict:
        """Xử lý truy vấn người dùng, trả về phản hồi JSON chuẩn hóa"""
        runnable_with_history = RunnableWithMessageHistory(
            self.chain,
            lambda: self._get_session_history(session_id),
            input_messages_key="input",
            history_messages_key="history"
        )
        timestamp = datetime.now(UTC).isoformat() + "Z"
        response = await runnable_with_history.ainvoke(
            {"input": query},
            config={"configurable": {"session_id": session_id}}
        )

        # Xử lý linh hoạt response
        if isinstance(response, LLMResult):
            response_text = json.loads(response.generations[0][0].text).get("response", "Lỗi phản hồi")
        elif isinstance(response, str):
            response_text = json.loads(response).get("response", "Lỗi phản hồi")
        else:
            response_text = "Lỗi định dạng phản hồi từ LLM"

        messages = [{
            "message_id": f"msg_{uuid.uuid4().hex[:8]}",
            "timestamp": timestamp,
            "sender": "chatbot",
            "text": response_text,
            "attachments": []
        }]
        context = {
            "conversation_state": "active",
            "intent": "conversation",
            "entities": {
                "input_query": query,
                "date": timestamp
            }
        }
        return build_chat_response(session_id, messages, context).model_dump()

    async def retrieve_chat_history(self, session_id: str, limit: Optional[int] = None) -> Dict:
        """Truy xuất lịch sử trò chuyện, trả về JSON chuẩn hóa"""
        timestamp = datetime.now(UTC).isoformat() + "Z"
        if session_id not in self.chat_histories:
            # Xử lý trường hợp không có lịch sử
            return build_chat_response(
                session_id,
                [],
                {
                    "conversation_state": "inactive",
                    "intent": "retrieve_history",
                    "entities": {"date": timestamp}
                }
            ).model_dump()

        history = self.chat_histories[session_id]
        messages = [message_to_dict(msg) for msg in history.messages]
        if limit:
            messages = messages[-limit * 2:]  # Giới hạn số cặp tin nhắn
        context = {
            "conversation_state": "active",
            "intent": "retrieve_history",
            "entities": {
                "total_messages": len(history.messages) // 2,
                "retrieved_count": len(messages) // 2,
                "date": timestamp
            }
        }
        # print(f"Context trước khi build: {context}")  # Thêm log để kiểm tra
        # response = build_chat_response(session_id, messages, context)
        # print(f"Response sau khi build: {response.model_dump()}")  # Thêm log để kiểm tra
        # return response.model_dump()
        return build_chat_response(session_id, messages, context).model_dump()

chatbot_service = ChatbotService()