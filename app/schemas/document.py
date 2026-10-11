from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentResponse(BaseModel):
    id: int
    filename: str
    file_type: str
    file_size: int
    status: str
    page_count: int | None
    document_category: str | None = None
    document_type: str | None = None
    department: str | None = None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class DocumentUploadResponse(BaseModel):
    id: int
    filename: str
    file_type: str
    file_size: int
    status: str
