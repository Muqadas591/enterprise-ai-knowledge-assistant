from fastapi.testclient import TestClient

from app.api.deps import get_db
from app.main import app
from app.services.conversation_service import ConversationService


def test_submit_feedback_creates_and_updates_rating():
    with TestClient(app) as client:
        email = "feedback-user@example.com"
        client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": "StrongPassword123"},
        )
        login = client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": "StrongPassword123"},
        )
        headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
        conversation_response = client.post(
            "/api/v1/conversations",
            headers=headers,
            json={"title": "Feedback test"},
        )
        conversation_id = conversation_response.json()["id"]

        db_generator = app.dependency_overrides[get_db]()
        db = next(db_generator)
        try:
            message = ConversationService(db).add_message(
                conversation_id=conversation_id,
                role="assistant",
                content="Initial answer",
            )
            message_id = message.id
        finally:
            db_generator.close()

        first = client.post(
            f"/api/v1/feedback/messages/{message_id}",
            headers=headers,
            json={"rating": "up", "comment": "Helpful"},
        )
        second = client.post(
            f"/api/v1/feedback/messages/{message_id}",
            headers=headers,
            json={"rating": "down", "comment": "Not relevant"},
        )

        assert first.status_code == 200
        assert second.status_code == 200
        assert first.json()["id"] == second.json()["id"]
        assert second.json()["rating"] == "down"
        assert second.json()["comment"] == "Not relevant"