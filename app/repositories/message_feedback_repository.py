from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.message_feedback import MessageFeedback


class MessageFeedbackRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_message_and_user(
        self,
        message_id: int,
        user_id: int,
    ) -> MessageFeedback | None:
        return self.db.scalar(
            select(MessageFeedback).where(
                MessageFeedback.message_id == message_id,
                MessageFeedback.user_id == user_id,
            )
        )

    def save(self, feedback: MessageFeedback) -> MessageFeedback:
        self.db.add(feedback)
        self.db.commit()
        self.db.refresh(feedback)
        return feedback
   


async def get_user_analytics(
    self,
    user_id: str,
):
    result = await self.db.execute(
        select(
            func.count(MessageFeedback.id),
            func.count(
                MessageFeedback.id
            ).filter(
                MessageFeedback.rating == "up"
            ),
            func.count(
                MessageFeedback.id
            ).filter(
                MessageFeedback.rating == "down"
            ),
        ).where(
            MessageFeedback.user_id == user_id
        )
    )

    total, positive, negative = (
        result.one()
    )

    return {
        "total_feedback": total or 0,
        "positive_feedback": positive or 0,
        "negative_feedback": negative or 0,
    }