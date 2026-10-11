import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import get_db
from app.main import app
from app.models.conversation import Conversation
from app.models.document import Document
from app.models.message import Message
from app.models.message_feedback import MessageFeedback
from app.models.password_reset_token import PasswordResetToken
from app.models.user import User


@pytest.fixture(scope="session", autouse=True)
def configure_test_database():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    Document.__table__.create(bind=engine)
    User.__table__.create(bind=engine)
    Conversation.__table__.create(bind=engine)
    Message.__table__.create(bind=engine)
    MessageFeedback.__table__.create(bind=engine)
    PasswordResetToken.__table__.create(bind=engine)

    def override_get_db():
        database = session_factory()

        try:
            yield database
        finally:
            database.close()

    app.dependency_overrides[get_db] = override_get_db

    yield

    app.dependency_overrides.pop(get_db, None)
    PasswordResetToken.__table__.drop(bind=engine)
    MessageFeedback.__table__.drop(bind=engine)
    User.__table__.drop(bind=engine)
    Message.__table__.drop(bind=engine)
    Conversation.__table__.drop(bind=engine)
    Document.__table__.drop(bind=engine)
