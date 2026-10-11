import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import select

from app.core.database import SessionLocal
from app.evaluation.retrieval_metrics import (
    mean_reciprocal_rank,
    recall_at_k,
    reciprocal_rank,
)
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.repositories.document_chunk_repository import DocumentChunkRepository
from app.schemas.retrieval_filters import RetrievalFilters
from app.services.hybrid_retrieval_service import HybridRetrievalService
from app.services.retrieval_service import RetrievalService


DEFAULT_DATASET = Path("evaluation/datasets/retrieval_eval.json")
DEFAULT_OUTPUT = Path("evaluation/results/retrieval_results.json")


def percentile(values: list[float], percentile_value: float) -> float:
    if not values:
        return 0.0

    ordered = sorted(values)
    position = (len(ordered) - 1) * percentile_value / 100
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower

    return ordered[lower] + (ordered[upper] - ordered[lower]) * fraction


def load_dataset(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def relevant_chunk_ids(session, item: dict) -> set[int]:
    document = session.execute(
        select(Document).where(Document.filename == item["relevant_document"])
    ).scalar_one_or_none()

    if document is None:
        return set()

    chunks = session.execute(
        select(DocumentChunk.id).where(
            DocumentChunk.document_id == document.id,
            DocumentChunk.chunk_index.in_(item["relevant_chunk_indices"]),
        )
    ).scalars().all()

    return set(chunks)


def evaluate_retriever(
    name: str,
    items: list[dict],
    session,
    search,
) -> dict:
    query_results = []
    latencies = []
    rankings = []
    relevant_sets = []

    for item in items:
        relevant = relevant_chunk_ids(session, item)
        started = time.perf_counter()
        results = search(item["query"])
        latency_ms = (time.perf_counter() - started) * 1000
        retrieved_ids = [chunk.id for chunk, document, score in results]

        latencies.append(latency_ms)
        rankings.append(retrieved_ids)
        relevant_sets.append(relevant)
        query_results.append(
            {
                "query": item["query"],
                "latency_ms": latency_ms,
                "recall_at_1": recall_at_k(retrieved_ids, relevant, 1),
                "recall_at_3": recall_at_k(retrieved_ids, relevant, 3),
                "recall_at_5": recall_at_k(retrieved_ids, relevant, 5),
                "reciprocal_rank": reciprocal_rank(retrieved_ids, relevant),
            }
        )

    return {
        "retriever": name,
        "recall_at_1": mean(item["recall_at_1"] for item in query_results),
        "recall_at_3": mean(item["recall_at_3"] for item in query_results),
        "recall_at_5": mean(item["recall_at_5"] for item in query_results),
        "mrr": mean_reciprocal_rank(rankings, relevant_sets),
        "average_latency_ms": mean(latencies) if latencies else 0.0,
        "p50_latency_ms": percentile(latencies, 50),
        "p95_latency_ms": percentile(latencies, 95),
        "queries": query_results,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate retrieval strategies.")
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    items = load_dataset(args.dataset)
    session = SessionLocal()

    try:
        repository = DocumentChunkRepository(session)
        vector_service = RetrievalService(session)
        hybrid_service = HybridRetrievalService(session)
        empty_filters = RetrievalFilters()

        evaluations = [
            evaluate_retriever(
                "vector",
                items,
                session,
                lambda query: vector_service.search(
                    query=query,
                    top_k=5,
                    filters=empty_filters,
                ),
            ),
            evaluate_retriever(
                "keyword",
                items,
                session,
                lambda query: repository.keyword_search(
                    query=query,
                    top_k=5,
                    filters=empty_filters,
                ),
            ),
            evaluate_retriever(
                "hybrid",
                items,
                session,
                lambda query: hybrid_service.search(
                    query=query,
                    top_k=5,
                    filters=empty_filters,
                ),
            ),
        ]
    finally:
        session.close()

    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dataset": str(args.dataset),
        "query_count": len(items),
        "evaluations": evaluations,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"Wrote retrieval evaluation to {args.output}")


if __name__ == "__main__":
    main()
