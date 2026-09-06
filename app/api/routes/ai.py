from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.ai import (
    AIAskRequest,
    AIAskResponse,
    AIResetRequest,
    AIResetResponse,
)
from app.services.ai_service import ai_service
from app.core.config import settings
from app.db.database import get_db

router = APIRouter(prefix="/ai", tags=["AI"])


def _ensure_openai_key() -> None:
    key = (settings.OPENAI_API_KEY or "").strip()
    if not key or key in ("your_openai_api_key_here", "your_api_key_here"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OPENAI_API_KEY chưa được cấu hình trên server",
        )


@router.post("/ask", response_model=AIAskResponse)
async def ask_ai(request: AIAskRequest, db: Session = Depends(get_db)):
    """
    Nhận câu hỏi từ Roblox → dùng brain riêng của player → gọi OpenAI → trả JSON.
    Tự động tạo brain mới nếu player chưa từng nói chuyện.
    """
    _ensure_openai_key()

    result = await ai_service.ask(
        db=db,
        question=request.question,
        player_id=request.player_id,
        player_name=request.player_name,
    )
    return result


@router.post("/reset", response_model=AIResetResponse)
def reset_brain(request: AIResetRequest, db: Session = Depends(get_db)):
    """
    Tạo brain mới cho đúng player_id (chỉ xóa memory của player đó).
    """
    success = ai_service.reset_brain(db, request.player_id)
    if not success:
        return AIResetResponse(
            success=True,
            player_id=request.player_id,
            message="Brain mới đã sẵn sàng (player chưa có lịch sử trước đó).",
        )
    return AIResetResponse(
        success=True,
        player_id=request.player_id,
        message="Đã tạo brain mới. Toàn bộ ký ức cũ đã được xóa.",
    )
