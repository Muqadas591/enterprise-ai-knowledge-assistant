from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models.conversation import Conversation
from app.models.message import Message
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository
from app.services.conversation_title_service import ConversationTitleService


class ConversationService:
    def __init__(self, db: Session):
        self.db = db
        self.conversations = ConversationRepository(db)
        self.messages = MessageRepository(db)

    def create_conversation(
        self,
        user_id: int,
        title: str = "New Conversation",
    ) -> Conversation:
        return self.conversations.create(
            Conversation(user_id=user_id, title=title),
        )

    def get_user_conversations(self, user_id: int) -> list[Conversation]:
        return self.conversations.get_by_user(user_id)

    def get_conversation(self, conversation_id: int) -> Conversation | None:
        return self.conversations.get_by_id(conversation_id)

    def verify_ownership(self, conversation_id: int, user_id: int) -> Conversation:
        conversation = self.conversations.get_by_id(conversation_id)
        if not conversation:
            raise ValueError("Conversation not found.")
        if conversation.user_id != user_id:
            raise PermissionError("You do not have access to this conversation.")
        return conversation

    def add_message(
        self,
        conversation_id: int,
        role: str,
        content: str,
        model: str | None = None,
        token_count: int | None = None,
    ) -> Message:
        message = self.messages.create(
            Message(
                conversation_id=conversation_id,
                role=role,
                content=content,
                model=model,
                token_count=token_count,
            ),
        )
        conversation = self.conversations.get_by_id(conversation_id)
        if conversation:
            conversation.updated_at = datetime.now(UTC)
            self.db.commit()
            self.db.refresh(conversation)
        return message

    def replace_assistant_message(
        self,
        message_id: int,
        conversation_id: int,
        content: str,
        model: str | None = None,
    ) -> Message:
        message = self.db.get(Message, message_id)
        if (
            message is None
            or message.conversation_id != conversation_id
            or message.role != "assistant"
        ):
            raise ValueError("Assistant message not found.")

        message.content = content
        message.model = model
        self.db.commit()
        self.db.refresh(message)
        return message

    def get_messages(self, conversation_id: int, limit: int = 50) -> list[Message]:
        return self.messages.get_by_conversation(conversation_id, limit=limit)

    def delete_conversation(self, conversation_id: int, user_id: int) -> None:
        conversation = self.verify_ownership(conversation_id, user_id)
        self.conversations.delete(conversation)

    def update_title_from_question(
        self,
        conversation: Conversation,
        question: str,
    ) -> Conversation:
        if conversation.title != "New Conversation":
            return conversation

        return self.conversations.update_title(
            conversation,
            ConversationTitleService.generate_title(question),
        )

    def search_conversations(self, user_id: int, query: str) -> list[Conversation]:
        return self.conversations.search_by_title(user_id=user_id, query=query)

    def update_conversation(
        self,
        conversation_id: int,
        user_id: int,
        title: str | None = None,
    ) -> Conversation:
        conversation = self.verify_ownership(conversation_id, user_id)
        if title is not None:
            return self.conversations.update_title(conversation, title)
        return conversation

    def archive_conversation(
        self,
        conversation_id: int,
        user_id: int,
    ) -> Conversation:
        conversation = self.verify_ownership(conversation_id, user_id)
        return self.conversations.archive(conversation)
