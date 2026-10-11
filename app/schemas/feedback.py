from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class FeedbackCreate(BaseModel):
    rating: Literal["up", "down"]
    comment: str | None = Field(
        default=None,
        max_length=1000,
    )


class FeedbackResponse(BaseModel):
    id: int
    message_id: int
    rating: str
    comment: str | None = None

    model_config = ConfigDict(from_attributes=True)