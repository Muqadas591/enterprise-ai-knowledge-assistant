from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


def auth_headers(client: TestClient, email: str) -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "StrongPassword123",
        },
    )
    assert response.status_code == 201

    login = client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": "StrongPassword123",
        },
    )
    assert login.status_code == 200
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def test_conversation_lifecycle_and_ownership():
    with TestClient(app) as client:
        owner_headers = auth_headers(client, f"owner-{uuid4().hex}@example.com")
        other_headers = auth_headers(client, f"other-{uuid4().hex}@example.com")

        created = client.post(
            "/api/v1/conversations",
            headers=owner_headers,
            json={"title": "Leave policy"},
        )
        assert created.status_code == 201
        conversation_id = created.json()["id"]

        owner_list = client.get("/api/v1/conversations", headers=owner_headers)
        assert owner_list.status_code == 200
        assert owner_list.json()[0]["id"] == conversation_id

        owner_detail = client.get(
            f"/api/v1/conversations/{conversation_id}",
            headers=owner_headers,
        )
        assert owner_detail.status_code == 200
        assert owner_detail.json()["messages"] == []

        other_detail = client.get(
            f"/api/v1/conversations/{conversation_id}",
            headers=other_headers,
        )
        assert other_detail.status_code == 403
