import pytest

from app.api.deps import get_db
from app.main import app
from app.models.user import User
from app.services.conversation_service import ConversationService


@pytest.fixture
def db():
    database_generator = app.dependency_overrides[get_db]()
    database = next(database_generator)
    try:
        yield database
    finally:
        database_generator.close()


def test_conversation_ownership_and_message_persistence(db):
    owner = User(
        email="service-owner@example.com",
        hashed_password="not-used-in-this-test",
    )
    other = User(
        email="service-other@example.com",
        hashed_password="not-used-in-this-test",
    )
    db.add_all([owner, other])
    db.commit()
    db.refresh(owner)
    db.refresh(other)

    service = ConversationService(db)
    conversation = service.create_conversation(owner.id, "Policy discussion")
    service.add_message(conversation.id, "user", "What is the leave policy?")
    service.add_message(
        conversation.id,
        "assistant",
        "Employees receive 20 days.",
        model="stub-model",
    )

    assert [message.role for message in service.get_messages(conversation.id)] == [
        "user",
        "assistant",
    ]
    assert service.verify_ownership(conversation.id, owner.id).id == conversation.id

    with pytest.raises(PermissionError):
        service.verify_ownership(conversation.id, other.id)


def test_nonexistent_conversation_is_rejected(db):
    with pytest.raises(ValueError):
        ConversationService(db).verify_ownership(999999, 1)
