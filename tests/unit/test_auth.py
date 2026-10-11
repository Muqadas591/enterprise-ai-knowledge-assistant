import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.api.dependencies import get_db
from app.core.security.hashing import hash_password
from app.core.security.roles import require_admin
from app.main import app
from app.models.user import User
from app.models.password_reset_token import PasswordResetToken


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def db():
    database_generator = app.dependency_overrides[get_db]()
    database = next(database_generator)
    try:
        yield database
    finally:
        database_generator.close()


def test_register_and_login(client: TestClient):
    registration = client.post(
        "/api/v1/auth/register",
        json={
            "email": "demo@example.com",
            "password": "StrongPassword123",
            "full_name": "Demo User",
        },
    )

    assert registration.status_code == 201
    assert registration.json()["role"] == "user"
    assert "hashed_password" not in registration.json()

    login = client.post(
        "/api/v1/auth/login",
        json={
            "email": "demo@example.com",
            "password": "StrongPassword123",
        },
    )

    assert login.status_code == 200
    assert login.json()["token_type"] == "bearer"
    assert login.json()["access_token"]


def test_protected_qa_requires_authentication(client: TestClient):
    response = client.post(
        "/api/v1/qa/ask",
        json={"question": "What is the leave policy?"},
    )

    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_forgot_password_response_does_not_reveal_account_existence(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(
        "app.api.routes.auth._send_reset_email",
        lambda email, token: None,
    )
    registration = client.post(
        "/api/v1/auth/register",
        json={"email": "reset-target@example.com", "password": "StrongPassword123"},
    )
    assert registration.status_code == 201

    known = client.post(
        "/api/v1/auth/forgot-password",
        json={"email": "reset-target@example.com"},
    )
    unknown = client.post(
        "/api/v1/auth/forgot-password",
        json={"email": "unknown-reset-target@example.com"},
    )

    assert known.status_code == 200
    assert unknown.status_code == 200
    assert known.json() == unknown.json()


def test_reset_password_token_is_hashed_expiring_and_single_use(
    client: TestClient,
    db,
    monkeypatch: pytest.MonkeyPatch,
):
    delivered = {}
    monkeypatch.setattr(
        "app.api.routes.auth._send_reset_email",
        lambda email, token: delivered.update(email=email, token=token),
    )
    email = "reset-flow@example.com"
    old_password = "OldStrongPassword123"
    new_password = "NewStrongPassword456"
    registration = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": old_password},
    )
    assert registration.status_code == 201

    forgot = client.post("/api/v1/auth/forgot-password", json={"email": email})
    assert forgot.status_code == 200
    assert delivered["email"] == email
    reset_token = db.scalar(
        select(PasswordResetToken).where(PasswordResetToken.user_id == registration.json()["id"])
    )
    assert reset_token is not None
    assert reset_token.token_hash != delivered["token"]

    reset = client.post(
        "/api/v1/auth/reset-password",
        json={"token": delivered["token"], "password": new_password},
    )
    assert reset.status_code == 200

    old_login = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": old_password},
    )
    new_login = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": new_password},
    )
    reused = client.post(
        "/api/v1/auth/reset-password",
        json={"token": delivered["token"], "password": "AnotherStrongPassword789"},
    )

    assert old_login.status_code == 401
    assert new_login.status_code == 200
    assert reused.status_code == 400


def test_admin_dependency_rejects_regular_user():
    user = User(email="employee@example.com", hashed_password=hash_password("password"))

    with pytest.raises(HTTPException) as error:
        require_admin(user)

    assert error.value.status_code == 403
