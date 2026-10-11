from pydantic import BaseModel, Field

from app.schemas.answer_quality import AnswerQuality
from app.schemas.observability import QAObservability


class SourceCitation(BaseModel):
    source_id: str
    document_id: int
    filename: str
    chunk_id: int
    chunk_index: int
    page_number: int | None = None


class QARequest(BaseModel):
    question: str = Field(min_length=3, max_length=2000)
    conversation_id: int | None = Field(default=None, ge=1)
    top_k: int = Field(default=5, ge=1, le=20)
    document_category: str | None = None
    document_type: str | None = None
    department: str | None = None
    document_id: int | None = Field(default=None, ge=1)
    regenerate: bool = False
    regenerate_message_id: int | None = Field(default=None, ge=1)


class QAResponse(BaseModel):
    conversation_id: int
    message_id: int | None = None
    answer: str
    model: str
    sources: list[SourceCitation]
    quality: AnswerQuality
    observability: QAObservability
