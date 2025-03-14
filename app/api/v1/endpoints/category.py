from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.service.chatbot_service import chatbot_service
from app.service.infer_category import CategoryInferencer
from app.utils.response_utils import ChatResponse

router = APIRouter(prefix="/category", tags=["category"])

class CategoryRequest(BaseModel):
    keywords: list[str]

category_inferencer = CategoryInferencer(llm=chatbot_service.llm)

@router.post("/infer", response_model=ChatResponse)
async def infer_category(request: CategoryRequest):
    """Suy luận danh mục từ từ khóa, trả về phản hồi chuẩn hóa"""
    if not request.keywords:
        raise HTTPException(status_code=400, detail="Keywords cannot be empty")
    result = await category_inferencer.infer_category(request.keywords)
    return ChatResponse(**result)