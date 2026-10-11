from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


def authenticate(client: TestClient, email: str) -> dict[str, str]:
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "StrongPassword123"},
    )
    login = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "StrongPassword123"},
    )
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def test_conversation_isolation_returns_forbidden():
    with TestClient(app) as client:
        owner = authenticate(client, f"owner-{uuid4().hex}@example.com")
        other = authenticate(client, f"other-{uuid4().hex}@example.com")

        created = client.post(
            "/api/v1/conversations",
            headers=owner,
            json={"title": "Private policy discussion"},
        )
        conversation_id = created.json()["id"]

        response = client.get(
            f"/api/v1/conversations/{conversation_id}",
            headers=other,
        )

        assert response.status_code == 403
