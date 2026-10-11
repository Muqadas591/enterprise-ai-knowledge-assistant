from collections import defaultdict


def reciprocal_rank_fusion(
    rankings: list[list[int]],
    k: int = 60,
) -> list[tuple[int, float]]:
    """Combine multiple ranked result lists using reciprocal rank fusion."""
    scores = defaultdict(float)

    for ranking in rankings:
        for rank, item_id in enumerate(ranking, start=1):
            scores[item_id] += 1.0 / (k + rank)

    return sorted(
        scores.items(),
        key=lambda item: item[1],
        reverse=True,
    )
