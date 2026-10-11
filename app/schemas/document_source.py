from typing import Optional

from pydantic import BaseModel


class DocumentSourceResponse(BaseModel):
    document_id: str
    filename: str

    chunk_index: int
    page_number: Optional[int] = None
    section_title: Optional[str] = None

    content: str