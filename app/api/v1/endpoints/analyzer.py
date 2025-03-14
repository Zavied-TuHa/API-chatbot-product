from fastapi import APIRouter, HTTPException
from app.service.chatbot_service import chatbot_service
from app.service.text_analyzer import TextAnalyzer
from app.utils.response_utils import ChatResponse
from app.utils.validation_utils import ChatRequest

router = APIRouter(prefix="/analyzer", tags=["analyzer"])

text_analyzer = TextAnalyzer(llm=chatbot_service.llm)

@router.post("/analyze", response_model=ChatResponse)
async def analyze_text(request: ChatRequest):
    """Xử lý truy vấn người dùng, phân loại và phân tích hoặc làm rõ"""
    query_type = await text_analyzer.classify_query(request.query)
    if "error" in query_type:
        raise HTTPException(status_code=500, detail=f"Không thể phân loại query: {query_type}")

    if query_type == "specific":
        # Phân tích truy vấn rõ ràng
        result = await text_analyzer.analyze(request.query)
    elif query_type == "ambiguous":
        # Làm rõ truy vấn mơ hồ
        result = await text_analyzer.clarify_ambiguous_query(request.query)
    else:
        raise HTTPException(status_code=500, detail="Không thể phân loại query")

    return ChatResponse(**result)
