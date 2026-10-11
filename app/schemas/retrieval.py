from pydantic import BaseModel


class RetrievalResult(BaseModel):
    chunk_id: int
    document_id: int
    chunk_index: int
    content: str
    page_number: int | None = None
    section_title: str | None = None
    score: float
    filename: str | None = None
    document_category: str | None = None
    document_type: str | None = None
    department: str | None = None


class RetrievalResponse(BaseModel):
    query: str
    results: list[RetrievalResult]
