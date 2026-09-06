from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.database import engine, Base
from app.models import Item, Player, Message  # noqa: F401 - đăng ký models
from app.api.routes import items
from app.api.routes import ai


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: tạo bảng nếu chưa có
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown (nếu cần)


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API Backend cho Roblox - nhận câu hỏi và trả lời bằng AI",
    lifespan=lifespan,
)

# CORS - cho phép frontend / Roblox gọi API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Trong production nên giới hạn domain cụ thể
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Đăng ký routes
app.include_router(items.router, prefix="/api/v1")
app.include_router(ai.router, prefix="/api/v1")


@app.get("/", tags=["Health"])
def root():
    return {
        "message": f"Chào mừng đến với {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "ai_endpoint": "/api/v1/ai/ask",
    }


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}
