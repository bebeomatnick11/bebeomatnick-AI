from pydantic import BaseModel, Field


class AIAskRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        examples=["Hôm nay bạn thế nào?"],
        description="Câu hỏi gửi tới AI",
    )
    player_id: str = Field(
        ...,
        min_length=1,
        max_length=64,
        examples=["123456789"],
        description="Roblox UserId (bắt buộc để nhận diện brain riêng)",
    )
    player_name: str | None = Field(
        None,
        max_length=100,
        examples=["NoobMaster69"],
        description="Tên hiển thị người chơi (tùy chọn)",
    )


class AIAskResponse(BaseModel):
    success: bool
    question: str
    answer: str
    model: str
    player_id: str
    player_name: str | None = None
    is_new_brain: bool = False


class AIResetRequest(BaseModel):
    player_id: str = Field(
        ...,
        min_length=1,
        max_length=64,
        description="Roblox UserId cần tạo brain mới",
    )


class AIResetResponse(BaseModel):
    success: bool
    player_id: str
    message: str
