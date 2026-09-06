from datetime import datetime

from sqlalchemy import String, Text, DateTime, Integer, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Player(Base):
    """Mỗi tài khoản Roblox = 1 brain / AI đồng hành"""
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    player_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    player_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    system_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)  # cá nhân hóa nếu muốn
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    messages: Mapped[list["Message"]] = relationship(
        "Message", back_populates="player", cascade="all, delete-orphan",
        order_by="Message.created_at"
    )


class Message(Base):
    """Lịch sử hội thoại của từng player"""
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    player_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("players.player_id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # user | assistant
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    player: Mapped["Player"] = relationship("Player", back_populates="messages")

    __table_args__ = (
        Index("ix_messages_player_created", "player_id", "created_at"),
    )
