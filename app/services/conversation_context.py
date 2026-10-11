from app.models.message import Message


class ConversationContextBuilder:
    def build(
        self,
        messages: list[Message],
        max_messages: int = 10,
    ) -> str:
        recent = messages[-max_messages:]
        return "\n".join(f"{message.role.upper()}: {message.content}" for message in recent)
