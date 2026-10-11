from typing import Any

from pydantic import BaseModel


class StreamEvent(BaseModel):
    type: str
    data: dict[str, Any]