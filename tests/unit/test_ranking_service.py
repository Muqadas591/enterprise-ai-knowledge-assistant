from app.services.ranking_service import reciprocal_rank_fusion


def test_rrf_combines_rankings():
    rankings = [
        [1, 2, 3],
        [2, 4, 1],
    ]

    results = reciprocal_rank_fusion(rankings)
    ranked_ids = [item_id for item_id, score in results]

    assert ranked_ids[0] == 2
