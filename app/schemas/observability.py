from pydantic import BaseModel


class QAObservability(BaseModel):
    request_id: str
    question: str
    retrieval_latency_ms: float
    llm_latency_ms: float
    total_latency_ms: float
    retrieved_chunks: int
    model: str
    token_usage: dict | None = None
    citation_count: int
    status: str
    error: str | None = None
