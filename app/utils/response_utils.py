from pydantic import BaseModel
from typing import List, Dict, Any
from langchain_core.messages import HumanMessage, BaseMessage
from datetime import datetime, UTC
import uuid, json

class Context(BaseModel):
    conversation_state: str
    intent: str
    entities: Dict[str, Any]

class ChatResponse(BaseModel):
    session_id: str
    messages: List[Dict[str, Any]]
    context: Context

def build_chat_response(session_id: str, messages: List[Dict], context: Dict) -> ChatResponse:
    # Chuẩn hóa phản hồi JSON theo định dạng mẫu
    return ChatResponse(
        session_id=session_id,
        messages=[
            {
                "message_id": msg.get("message_id", f"msg_{uuid.uuid4().hex[:8]}"),  # Tạo message_id nếu chưa có
                "timestamp": msg.get("timestamp", datetime.now(UTC).isoformat() + "Z"),  # Gán timestamp mặc định nếu thiếu
                "sender": msg["sender"],
                "text": msg["text"],
                "attachments": msg.get("attachments", [])  # Đảm bảo attachments luôn có, mặc định rỗng
            }
            for msg in messages
        ],
        context=Context(
            conversation_state=context["conversation_state"],
            intent=context["intent"],
            entities=context["entities"]
        )
    )

def message_to_dict(message: BaseMessage) -> Dict[str, Any]:
    """Chuyển đổi LangChain BaseMessage thành dict để dùng trong messages"""
    sender = "user" if isinstance(message, HumanMessage) else "chatbot"
    text = message.content if sender == "user" else json.loads(message.content).get("response", "Lỗi phản hồi") if isinstance(message.content, str) else "Lỗi định dạng"
    return {
        "message_id": f"msg_{uuid.uuid4().hex[:8]}",
        "timestamp": datetime.now(UTC).isoformat() + "Z",
        "sender": sender,
        "text": text,
        "attachments": []  # Mặc định rỗng, có thể mở rộng sau
    }