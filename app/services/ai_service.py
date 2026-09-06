from openai import AsyncOpenAI, APITimeoutError, APIError, RateLimitError
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.player import Player, Message


MAX_HISTORY_MESSAGES = 12


class AIService:
    def __init__(self):
        self._client: AsyncOpenAI | None = None

    @property
    def client(self) -> AsyncOpenAI:
        if self._client is None:
            key = (settings.OPENAI_API_KEY or "").strip()
            if not key or key in ("your_openai_api_key_here", "your_api_key_here"):
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="OPENAI_API_KEY chưa được cấu hình trên server",
                )
            self._client = AsyncOpenAI(
                api_key=key,
                base_url=settings.OPENAI_BASE_URL,
                timeout=45.0,
            )
        return self._client

    def get_or_create_player(
        self,
        db: Session,
        player_id: str,
        player_name: str | None = None,
    ) -> tuple[Player, bool]:
        player = db.query(Player).filter(Player.player_id == player_id).first()
        if player:
            if player_name and player.player_name != player_name:
                player.player_name = player_name
                db.commit()
            return player, False

        player = Player(player_id=player_id, player_name=player_name)
        db.add(player)
        db.commit()
        db.refresh(player)
        return player, True

    def get_recent_messages(self, db: Session, player_id: str) -> list[dict]:
        rows = (
            db.query(Message)
            .filter(Message.player_id == player_id)
            .order_by(Message.created_at.desc())
            .limit(MAX_HISTORY_MESSAGES)
            .all()
        )
        rows = list(reversed(rows))
        return [{"role": m.role, "content": m.content} for m in rows]

    def save_message(self, db: Session, player_id: str, role: str, content: str) -> None:
        msg = Message(player_id=player_id, role=role, content=content)
        db.add(msg)
        db.commit()

    def reset_brain(self, db: Session, player_id: str) -> bool:
        """Chỉ xóa messages của player_id được chỉ định. Không ảnh hưởng player khác."""
        player = db.query(Player).filter(Player.player_id == player_id).first()
        if not player:
            return False
        db.query(Message).filter(Message.player_id == player_id).delete()
        db.commit()
        return True

    async def ask(
        self,
        db: Session,
        question: str,
        player_id: str,
        player_name: str | None = None,
    ) -> dict:
        try:
            player, is_new = self.get_or_create_player(db, player_id, player_name)
            history = self.get_recent_messages(db, player_id)

            system_prompt = player.system_prompt or settings.OPENAI_SYSTEM_PROMPT
            if player_name:
                system_prompt = (
                    f"{system_prompt}\n"
                    f"Bạn đang nói chuyện với người chơi tên {player_name} trong Roblox."
                )

            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(history)
            messages.append({"role": "user", "content": question})

            answer = await self._call_ai(messages)

            self.save_message(db, player_id, "user", question)
            self.save_message(db, player_id, "assistant", answer)

            return {
                "success": True,
                "question": question,
                "answer": answer.strip(),
                "model": settings.OPENAI_MODEL,
                "player_id": player_id,
                "player_name": player.player_name or player_name,
                "is_new_brain": is_new,
            }

        except HTTPException:
            raise
        except APITimeoutError:
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="OpenAI API timeout - vui lòng thử lại",
            )
        except RateLimitError:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="OpenAI rate limit - vui lòng thử lại sau",
            )
        except APIError as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Lỗi từ OpenAI: {str(e)}",
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Lỗi khi gọi OpenAI API: {str(e)}",
            )

    async def _call_ai(self, messages: list[dict]) -> str:
        """Ưu tiên OpenAI Responses API, fallback Chat Completions."""
        try:
            input_messages = [
                {"role": m["role"], "content": m["content"]} for m in messages
            ]
            response = await self.client.responses.create(
                model=settings.OPENAI_MODEL,
                input=input_messages,
            )
            if hasattr(response, "output_text") and response.output_text:
                return response.output_text
            if hasattr(response, "output") and response.output:
                for item in response.output:
                    if getattr(item, "type", None) == "message":
                        for content in getattr(item, "content", []) or []:
                            if getattr(content, "type", None) == "output_text":
                                return getattr(content, "text", "") or ""
            return ""
        except Exception:
            # Fallback Chat Completions
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=messages,
                temperature=0.7,
                max_tokens=1024,
            )
            return response.choices[0].message.content or ""


ai_service = AIService()
