from pydantic import BaseModel


class RetrievalFilters(BaseModel):
    document_category: str | None = None
    document_type: str | None = None
    department: str | None = None
    document_id: int | None = None
