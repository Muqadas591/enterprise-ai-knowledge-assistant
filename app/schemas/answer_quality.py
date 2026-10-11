from pydantic import BaseModel


class AnswerQuality(BaseModel):
    confidence: str
    confidence_score: int
    citation_quality: str
    source_count: int