from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.conversation import Conversation


class ConversationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, conversation: Conversation) -> Conversation:
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        return conversation

    def get_by_id(self, conversation_id: int) -> Conversation | None:
        statement = select(Conversation).where(Conversation.id == conversation_id)
        return self.db.scalar(statement)

    def get_by_user(self, user_id: int) -> list[Conversation]:
        statement = (
            select(Conversation)
            .where(
                Conversation.user_id == user_id,
                Conversation.is_archived.is_(False),
            )
            .order_by(Conversation.updated_at.desc())
        )
        return list(self.db.scalars(statement).all())

    def search_by_title(self, user_id: int, query: str) -> list[Conversation]:
        statement = (
            select(Conversation)
            .where(
                Conversation.user_id == user_id,
                Conversation.title.ilike(f"%{query}%"),
                Conversation.is_archived.is_(False),
            )
            .order_by(Conversation.updated_at.desc())
        )
        return list(self.db.scalars(statement).all())

    def update_title(self, conversation: Conversation, title: str) -> Conversation:
        conversation.title = title.strip()
        self.db.commit()
        self.db.refresh(conversation)
        return conversation

    def archive(self, conversation: Conversation) -> Conversation:
        conversation.is_archived = True
        self.db.commit()
        self.db.refresh(conversation)
        return conversation

    def delete(self, conversation: Conversation) -> None:
        self.db.delete(conversation)
        self.db.commit()
