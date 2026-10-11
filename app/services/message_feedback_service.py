from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.message import Message
from app.repositories.message_feedback_repository import (
    MessageFeedbackRepository,
)


class MessageFeedbackService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = MessageFeedbackRepository(db)

    async def submit_feedback(
        self,
        message_id: str,
        user_id: str,
        rating: str,
        comment: str | None = None,
    ):
        message = await self.db.get(Message, message_id)

        if message is None:
            raise HTTPException(
                status_code=404,
                detail="Message not found.",
            )

        # Ownership check through conversation
        conversation = message.conversation

        if conversation is None:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found.",
            )

        if str(conversation.user_id) != str(user_id):
            raise HTTPException(
                status_code=403,
                detail="You do not have access to this message.",
            )

        existing = await self.repository.get_by_message_and_user(
            message_id=message_id,
            user_id=user_id,
        )

        if existing:
            return await self.repository.update(
                feedback=existing,
                rating=rating,
                comment=comment,
            )

        return await self.repository.create(
            message_id=message_id,
            user_id=user_id,
            rating=rating,
            comment=comment,
        )
async def get_analytics(
    self,
    user_id: str,
):
    data = await self.repository.get_user_analytics(
        user_id=user_id
    )

    total = data["total_feedback"]
    positive = data["positive_feedback"]

    positive_rate = (
        round(
            (positive / total) * 100,
            2,
        )
        if total > 0
        else 0.0
    )

    return {
        **data,
        "positive_rate": positive_rate,
    }