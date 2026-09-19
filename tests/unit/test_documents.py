from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_documents_endpoint() -> None:
    response = client.get("/api/v1/documents")

    assert response.status_code == 200

    assert response.json() == {"message": "Document API initialized."}
