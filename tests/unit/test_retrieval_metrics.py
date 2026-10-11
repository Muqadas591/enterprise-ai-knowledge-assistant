from app.evaluation.retrieval_metrics import (
    mean_reciprocal_rank,
    recall_at_k,
    reciprocal_rank,
)


def test_recall_at_1():
    retrieved = [10, 20, 30]
    relevant = {10}

    assert recall_at_k(retrieved, relevant, 1) == 1.0


def test_recall_at_3():
    retrieved = [10, 20, 30]
    relevant = {30}

    assert recall_at_k(retrieved, relevant, 3) == 1.0


def test_recall_miss():
    retrieved = [10, 20, 30]
    relevant = {40}

    assert recall_at_k(retrieved, relevant, 3) == 0.0


def test_reciprocal_rank():
    retrieved = [10, 20, 30]
    relevant = {20}

    assert reciprocal_rank(retrieved, relevant) == 0.5


def test_mrr():
    rankings = [
        [10, 20, 30],
        [40, 60, 50],
    ]

    relevant_sets = [
        {10},
        {60},
    ]

    assert mean_reciprocal_rank(rankings, relevant_sets) == 0.75
