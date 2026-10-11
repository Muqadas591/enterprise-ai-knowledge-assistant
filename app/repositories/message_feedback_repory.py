from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.message_feedback import MessageFeedback


class MessageFeedbackRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_message_and_user(
        self,
        message_id: str,
        user_id: str,
    ):
        result = await self.db.execute(
            select(MessageFeedback).where(
                MessageFeedback.message_id == message_id,
                MessageFeedback.user_id == user_id,
            )
        )

        return result.scalar_one_or_none()

    async def create(
        self,
        message_id: str,
        user_id: str,
        rating: str,
        comment: str | None = None,
    ):
        feedback = MessageFeedback(
            message_id=message_id,
            user_id=user_id,
            rating=rating,
            comment=comment,
        )

        self.db.add(feedback)

        await self.db.commit()
        await self.db.refresh(feedback)

        return feedback

    async def update(
        self,
        feedback: MessageFeedback,
        rating: str,
        comment: str | None = None,
    ):
        feedback.rating = rating
        feedback.comment = comment

        await self.db.commit()
        await self.db.refresh(feedback)

        return feedback