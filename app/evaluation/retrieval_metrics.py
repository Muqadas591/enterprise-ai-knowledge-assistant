from collections.abc import Sequence
from dataclasses import dataclass


@dataclass
class RetrievalMetrics:
    recall_at_1: float
    recall_at_3: float
    recall_at_5: float
    mrr: float
    average_latency_ms: float


def recall_at_k(
    retrieved: Sequence[int],
    relevant: set[int],
    k: int,
) -> float:
    """
    Returns 1 if at least one relevant item appears in the top-k results.
    """
    if not relevant:
        return 0.0

    retrieved_top_k = set(retrieved[:k])

    return float(bool(retrieved_top_k.intersection(relevant)))


def reciprocal_rank(
    retrieved: Sequence[int],
    relevant: set[int],
) -> float:
    """Return reciprocal rank of the first relevant result."""
    if not relevant:
        return 0.0

    for rank, item_id in enumerate(retrieved, start=1):
        if item_id in relevant:
            return 1.0 / rank

    return 0.0


def mean_reciprocal_rank(
    rankings: list[Sequence[int]],
    relevant_sets: list[set[int]],
) -> float:
    if not rankings:
        return 0.0

    scores = [
        reciprocal_rank(ranking, relevant) for ranking, relevant in zip(rankings, relevant_sets)
    ]

    return sum(scores) / len(scores)
