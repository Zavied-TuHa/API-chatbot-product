from fastapi import Depends, HTTPException
from pydantic import BaseModel, constr

class ChatRequest(BaseModel):
    query: constr(min_length=1, strip_whitespace=True)  # Validation trực tiếp: query không được rỗng
    session_id: constr(min_length=1, strip_whitespace=True) | None = None  # session_id tùy chọn

class HistoryRequest(BaseModel):
    session_id: constr(min_length=1, strip_whitespace=True)  # Validation trực tiếp: session_id bắt buộc
    limit: int | None = None  # Giới hạn số tin nhắn, tùy chọn

# Dependency để tái sử dụng validation session_id nếu cần trong các endpoint khác
def validate_session_id(session_id: str = Depends(lambda x: x)):
    if not session_id or not session_id.strip():
        raise HTTPException(status_code=400, detail="Session ID cannot be empty")
    return session_id