from app.schemas.retrieval import RetrievalResult
from app.services.context_builder import ContextBuilder


def test_context_builder_creates_citation_sources():
    result = RetrievalResult(
        chunk_id=7,
        document_id=3,
        chunk_index=2,
        content="Employees receive annual leave.",
        page_number=1,
        score=0.9,
        filename="leave_policy.txt",
    )

    context, sources = ContextBuilder().build([result])

    assert sources[0].source_id == "S1"
    assert sources[0].chunk_index == 2
    assert "[S1]" in context
    assert "Document: leave_policy.txt" in context
    assert "Chunk Index: 2" in context
