from pydantic import BaseModel


class FeedbackAnalyticsResponse(BaseModel):
    total_feedback: int
    positive_feedback: int
    negative_feedback: int
    positive_rate: float