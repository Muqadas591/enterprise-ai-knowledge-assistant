from app.schemas.retrieval import RetrievalResult
from app.services.rag_service import RAGService
from tests.mocks.fake_llm import FakeLLMService


class FakeRetrievalService:
    def __init__(self, results):
        self.results = results
        self.calls = []

    def search(self, query, top_k, filters):
        self.calls.append((query, top_k, filters))
        return self.results


def test_rag_service_builds_grounded_answer_and_sources():
    retrieval = FakeRetrievalService(
        [
            RetrievalResult(
                chunk_id=7,
                document_id=3,
                chunk_index=0,
                content="Employees receive 24 annual leave days.",
                score=0.9,
                filename="leave_policy.txt",
            )
        ]
    )
    service = RAGService(retrieval, FakeLLMService())

    result = service.answer("How many annual leave days are available?")

    assert result.answer == "Test answer [S1]"
    assert result.model == "fake-model"
    assert result.sources[0].source_id == "S1"
    assert result.observability.request_id
    assert result.observability.status == "success"
    assert result.observability.retrieved_chunks == 1
    assert result.observability.citation_count == 1
    assert result.observability.total_latency_ms >= 0
    assert retrieval.calls[0][0] == "How many annual leave days are available?"


def test_rag_service_refuses_to_invent_without_results():
    service = RAGService(FakeRetrievalService([]), FakeLLMService())

    result = service.answer("What is the private jet policy?")

    assert "could not find relevant information" in result.answer
    assert result.sources == []
    assert result.model == "FakeLLMService"
    assert result.observability.status == "no_results"
    assert result.observability.retrieved_chunks == 0
