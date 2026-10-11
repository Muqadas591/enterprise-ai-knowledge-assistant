class AnswerQualityService:

    @staticmethod
    def calculate(
        sources: list,
        retrieval_scores: list[float] | None = None,
    ) -> dict:

        source_count = len(sources)

        if source_count == 0:
            return {
                "confidence": "low",
                "confidence_score": 0,
                "citation_quality": "none",
                "source_count": 0,
            }

        scores = retrieval_scores or []

        if scores:
            top_score = max(scores)
        else:
            top_score = 0.0

        if source_count >= 3 and top_score >= 0.75:
            confidence = "high"
            confidence_score = 90

        elif source_count >= 2 and top_score >= 0.60:
            confidence = "medium"
            confidence_score = 70

        elif source_count >= 1:
            confidence = "low"
            confidence_score = 45

        else:
            confidence = "low"
            confidence_score = 0

        if source_count >= 3:
            citation_quality = "strong"

        elif source_count >= 1:
            citation_quality = "supported"

        else:
            citation_quality = "none"

        return {
            "confidence": confidence,
            "confidence_score": confidence_score,
            "citation_quality": citation_quality,
            "source_count": source_count,
        }