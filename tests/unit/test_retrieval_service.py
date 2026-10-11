import pytest

from app.services.retrieval_service import RetrievalService


def test_empty_query_is_rejected():
    service = RetrievalService.__new__(RetrievalService)

    with pytest.raises(ValueError):
        service.search("")
