from typing import ClassVar
from uuid import uuid4

from fastapi.testclient import TestClient

from app.llm.base import LLMResponse
from app.main import app
from app.schemas.retrieval import RetrievalResult


class WorkflowLLM:
    def __init__(self):
        self.rewrite_prompts: list[str] = []

    def generate(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        if "standalone" in user_prompt:
            self.rewrite_prompts.append(user_prompt)
            return LLMResponse(
                content="annual leave policy for probationary employees",
                model="workflow-model",
            )
        return LLMResponse(content="Answer", model="workflow-model")


class EmptyRetrieval:
    queries: ClassVar[list[str]] = []

    def __init__(self, db):
        self.db = db

    def search(self, query, top_k, filters):
        self.queries.append(query)
        return []


class StreamingWorkflowLLM(WorkflowLLM):
    def __init__(self):
        super().__init__()
        self.stream_calls = 0

    async def stream(self, system_prompt: str, user_prompt: str):
        self.stream_calls += 1
        if self.stream_calls == 1:
            yield "Streamed "
            yield "answer [S1]"
        else:
            yield "Regenerated "
            yield "answer [S1]"


class StreamingRetrieval:
    def __init__(self, db):
        self.db = db

    def search(self, query, top_k, filters):
        return [
            RetrievalResult(
                chunk_id=7,
                document_id=3,
                chunk_index=0,
                content="MFA is required.",
                score=0.9,
                filename="it_policy.txt",
            )
        ]


def login(client: TestClient, email: str) -> dict[str, str]:
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "StrongPassword123"},
    )
    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "StrongPassword123"},
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_multi_turn_qa_rewrites_and_persists_messages(monkeypatch):
    import app.api.routes.qa as qa_route

    llm = WorkflowLLM()
    EmptyRetrieval.queries = []
    monkeypatch.setattr(qa_route, "get_llm_service", lambda: llm)
    monkeypatch.setattr(qa_route, "HybridRetrievalService", EmptyRetrieval)

    with TestClient(app) as client:
        headers = login(client, f"qa-{uuid4().hex}@example.com")
        first = client.post(
            "/api/v1/qa/ask",
            headers=headers,
            json={"question": "What is the annual leave policy?"},
        )
        assert first.status_code == 200
        conversation_id = first.json()["conversation_id"]

        second = client.post(
            "/api/v1/qa/ask",
            headers=headers,
            json={
                "conversation_id": conversation_id,
                "question": "What about probationary employees?",
            },
        )
        assert second.status_code == 200
        assert EmptyRetrieval.queries[-1] == ("annual leave policy for probationary employees")
        assert len(llm.rewrite_prompts) == 2
        assert "What is the annual leave policy?" in llm.rewrite_prompts[-1]

        detail = client.get(
            f"/api/v1/conversations/{conversation_id}",
            headers=headers,
        )
        assert [message["role"] for message in detail.json()["messages"]] == [
            "user",
            "assistant",
            "user",
            "assistant",
        ]


def test_streaming_qa_emits_events_and_persists_answer(monkeypatch):
    import json
    import app.api.routes.qa as qa_route

    llm = StreamingWorkflowLLM()
    monkeypatch.setattr(qa_route, "get_llm_service", lambda: llm)
    monkeypatch.setattr(qa_route, "HybridRetrievalService", StreamingRetrieval)

    with TestClient(app) as client:
        headers = login(client, f"qa-stream-{uuid4().hex}@example.com")
        response = client.post(
            "/api/v1/qa/ask/stream",
            headers=headers,
            json={"question": "What does the policy require?"},
        )

        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/event-stream")
        events = [
            json.loads(line.removeprefix("data: "))
            for line in response.text.splitlines()
            if line.startswith("data: ")
        ]
        assert [event["type"] for event in events] == ["token", "token", "sources", "done"]
        assert events[2]["data"]["sources"][0]["filename"] == "it_policy.txt"
        assert events[-1]["data"]["conversation_id"]
        conversation_id = events[-1]["data"]["conversation_id"]

        detail = client.get(
            f"/api/v1/conversations/{conversation_id}",
            headers=headers,
        )
        assert detail.status_code == 200
        assert detail.json()["messages"][-1]["content"] == "Streamed answer [S1]"
        assistant_id = events[-1]["data"]["assistant_message_id"]

        regenerated = client.post(
            "/api/v1/qa/ask/stream",
            headers=headers,
            json={
                "conversation_id": conversation_id,
                "question": "What does the policy require?",
                "regenerate": True,
                "regenerate_message_id": assistant_id,
            },
        )
        assert regenerated.status_code == 200

        updated_detail = client.get(
            f"/api/v1/conversations/{conversation_id}",
            headers=headers,
        )
        updated_messages = updated_detail.json()["messages"]
        assert [message["role"] for message in updated_messages] == ["user", "assistant"]
        assert updated_messages[-1]["id"] == assistant_id
        assert updated_messages[-1]["content"] == "Regenerated answer [S1]"
