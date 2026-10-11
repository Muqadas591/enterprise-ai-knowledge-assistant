from types import SimpleNamespace

from app.services.conversation_context import ConversationContextBuilder


def message(role: str, content: str):
    return SimpleNamespace(role=role, content=content)


def test_history_formatting():
    history = ConversationContextBuilder().build(
        [message("user", "What is leave?"), message("assistant", "Twenty days.")]
    )

    assert history == "USER: What is leave?\nASSISTANT: Twenty days."


def test_history_limit_uses_most_recent_messages():
    messages = [message("user", f"Question {index}") for index in range(12)]

    history = ConversationContextBuilder().build(messages, max_messages=10)
    lines = history.splitlines()

    assert lines[0] == "USER: Question 2"
    assert lines[-1] == "USER: Question 11"
    assert len(lines) == 10
