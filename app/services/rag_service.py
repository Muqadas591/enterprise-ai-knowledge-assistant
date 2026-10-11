import json
import logging
import time
from collections.abc import AsyncIterator
from dataclasses import dataclass
from uuid import uuid4

from app.llm.base import LLMService
from app.rag.prompts.rag_prompt import (
    RAG_SYSTEM_PROMPT,
    build_rag_user_prompt,
)
from app.schemas.observability import QAObservability
from app.schemas.retrieval import RetrievalResult
from app.schemas.answer_quality import AnswerQuality
from app.services.answer_quality_service import AnswerQualityService
from app.services.context_builder import ContextBuilder, ContextSource

logger = logging.getLogger(__name__)


@dataclass
class RAGAnswer:
    answer: str
    sources: list[ContextSource]
    model: str
    observability: QAObservability
    quality: AnswerQuality


class RAGService:
    def __init__(
        self,
        retrieval_service,
        llm_service: LLMService,
    ) -> None:
        self.retrieval_service = retrieval_service
        self.llm_service = llm_service
        self.context_builder = ContextBuilder()

    def _to_retrieval_results(self, retrieval_response) -> list[RetrievalResult]:
        if hasattr(retrieval_response, "results"):
            return retrieval_response.results

        if all(isinstance(result, RetrievalResult) for result in retrieval_response):
            return retrieval_response

        return [
            RetrievalResult(
                chunk_id=chunk.id,
                document_id=chunk.document_id,
                chunk_index=chunk.chunk_index,
                content=chunk.content,
                page_number=chunk.page_number,
                section_title=chunk.section_title,
                score=float(score),
                filename=document.filename,
                document_category=document.document_category,
                document_type=document.document_type,
                department=document.department,
            )
            for chunk, document, score in retrieval_response
        ]

    def _retrieve_context(
        self,
        query: str,
        top_k: int,
        filters,
    ) -> tuple[list[RetrievalResult], str, list[ContextSource]]:
        retrieval_response = self.retrieval_service.search(
            query=query,
            top_k=top_k,
            filters=filters,
        )
        results = self._to_retrieval_results(retrieval_response)
        if not results:
            return results, "", []

        context, sources = self.context_builder.build(results)
        return results, context, sources

    def answer(
        self,
        question: str,
        top_k: int = 5,
        filters=None,
        request_id: str | None = None,
        retrieval_query: str | None = None,
    ) -> RAGAnswer:
        if not question.strip():
            raise ValueError("Question cannot be empty.")

        request_id = request_id or str(uuid4())
        started = time.perf_counter()
        retrieval_started = time.perf_counter()
        retrieval_latency_ms = 0.0
        retrieval_finished = False
        llm_latency_ms = 0.0
        results: list[RetrievalResult] = []
        model = self.llm_service.__class__.__name__

        try:
            results, context, sources = self._retrieve_context(
                query=retrieval_query or question,
                top_k=top_k,
                filters=filters,
            )
            retrieval_latency_ms = (time.perf_counter() - retrieval_started) * 1000
            retrieval_finished = True

            if not results:
                quality = AnswerQuality(**AnswerQualityService.calculate(sources=[]))
                observation = QAObservability(
                    request_id=request_id,
                    question=question,
                    retrieval_latency_ms=retrieval_latency_ms,
                    llm_latency_ms=0.0,
                    total_latency_ms=(time.perf_counter() - started) * 1000,
                    retrieved_chunks=0,
                    model=model,
                    citation_count=0,
                    status="no_results",
                )
                self._log_observation(observation)
                return RAGAnswer(
                    answer=("I could not find relevant information in the available documents."),
                    sources=[],
                    model=model,
                    observability=observation,
                    quality=quality,
                )

            user_prompt = build_rag_user_prompt(
                question=question,
                context=context,
            )
            llm_started = time.perf_counter()
            llm_response = self.llm_service.generate(
                system_prompt=RAG_SYSTEM_PROMPT,
                user_prompt=user_prompt,
            )
            llm_latency_ms = (time.perf_counter() - llm_started) * 1000
            quality = AnswerQuality(
                **AnswerQualityService.calculate(
                    sources=sources,
                    retrieval_scores=[result.score for result in results],
                )
            )
            observation = QAObservability(
                request_id=request_id,
                question=question,
                retrieval_latency_ms=retrieval_latency_ms,
                llm_latency_ms=llm_latency_ms,
                total_latency_ms=(time.perf_counter() - started) * 1000,
                retrieved_chunks=len(results),
                model=llm_response.model,
                token_usage=llm_response.usage,
                citation_count=len(sources),
                status="success",
            )
            self._log_observation(observation)

            return RAGAnswer(
                answer=llm_response.content,
                sources=sources,
                model=llm_response.model,
                observability=observation,
                quality=quality,
            )
        except Exception as exc:
            if not retrieval_finished:
                retrieval_latency_ms = (time.perf_counter() - retrieval_started) * 1000

            observation = QAObservability(
                request_id=request_id,
                question=question,
                retrieval_latency_ms=retrieval_latency_ms,
                llm_latency_ms=llm_latency_ms,
                total_latency_ms=(time.perf_counter() - started) * 1000,
                retrieved_chunks=len(results),
                model=model,
                citation_count=0,
                status="error",
                error=str(exc),
            )
            self._log_observation(observation, level=logging.ERROR)
            raise

    async def stream_answer(
        self,
        question: str,
        top_k: int = 5,
        filters=None,
        request_id: str | None = None,
        retrieval_query: str | None = None,
    ) -> AsyncIterator[dict]:
        if not question.strip():
            raise ValueError("Question cannot be empty.")

        request_id = request_id or str(uuid4())
        started = time.perf_counter()
        retrieval_started = time.perf_counter()
        llm_latency_ms = 0.0
        results: list[RetrievalResult] = []
        model = self.llm_service.__class__.__name__

        try:
            results, context, sources = self._retrieve_context(
                query=retrieval_query or question,
                top_k=top_k,
                filters=filters,
            )
            retrieval_latency_ms = (time.perf_counter() - retrieval_started) * 1000

            if not results:
                quality = AnswerQuality(**AnswerQualityService.calculate(sources=[]))
                observation = QAObservability(
                    request_id=request_id,
                    question=question,
                    retrieval_latency_ms=retrieval_latency_ms,
                    llm_latency_ms=0.0,
                    total_latency_ms=(time.perf_counter() - started) * 1000,
                    retrieved_chunks=0,
                    model=model,
                    citation_count=0,
                    status="no_results",
                )
                self._log_observation(observation)
                yield {
                    "type": "token",
                    "data": {
                        "text": "I could not find relevant information in the available documents."
                    },
                }
                yield {"type": "sources", "data": {"sources": []}}
                yield {"type": "quality", "data": quality.model_dump()}
                yield {
                    "type": "done",
                    "data": {
                        "model": model,
                        "quality": quality.model_dump(),
                        "observability": observation.model_dump(),
                    },
                }
                return

            serialized_sources = [
                {
                    "source_id": source.source_id,
                    "document_id": source.document_id,
                    "filename": source.filename,
                    "chunk_id": source.chunk_id,
                    "chunk_index": source.chunk_index,
                    "page_number": source.page_number,
                }
                for source in sources
            ]
            user_prompt = build_rag_user_prompt(question=question, context=context)
            llm_started = time.perf_counter()
            full_answer = ""
            stream = getattr(self.llm_service, "stream", None)
            if stream is None:
                response = self.llm_service.generate(
                    system_prompt=RAG_SYSTEM_PROMPT,
                    user_prompt=user_prompt,
                )
                model = response.model
                if response.content:
                    full_answer += response.content
                    yield {"type": "token", "data": {"text": response.content}}
            else:
                async for token in stream(
                    system_prompt=RAG_SYSTEM_PROMPT,
                    user_prompt=user_prompt,
                ):
                    if token:
                        full_answer += token
                        yield {"type": "token", "data": {"text": token}}

            llm_latency_ms = (time.perf_counter() - llm_started) * 1000
            if not full_answer:
                raise RuntimeError("The LLM provider returned an empty response.")

            quality = AnswerQuality(
                **AnswerQualityService.calculate(
                    sources=sources,
                    retrieval_scores=[result.score for result in results],
                )
            )

            observation = QAObservability(
                request_id=request_id,
                question=question,
                retrieval_latency_ms=retrieval_latency_ms,
                llm_latency_ms=llm_latency_ms,
                total_latency_ms=(time.perf_counter() - started) * 1000,
                retrieved_chunks=len(results),
                model=model,
                citation_count=len(sources),
                status="success",
            )
            self._log_observation(observation)
            yield {"type": "sources", "data": {"sources": serialized_sources}}
            yield {"type": "quality", "data": quality.model_dump()}
            yield {
                "type": "done",
                "data": {
                    "model": model,
                    "quality": quality.model_dump(),
                    "observability": observation.model_dump(),
                },
            }
        except Exception as exc:
            retrieval_latency_ms = (time.perf_counter() - retrieval_started) * 1000
            observation = QAObservability(
                request_id=request_id,
                question=question,
                retrieval_latency_ms=retrieval_latency_ms,
                llm_latency_ms=llm_latency_ms,
                total_latency_ms=(time.perf_counter() - started) * 1000,
                retrieved_chunks=len(results),
                model=model,
                citation_count=0,
                status="error",
                error=str(exc),
            )
            self._log_observation(observation, level=logging.ERROR)
            raise

    @staticmethod
    def _log_observation(
        observation: QAObservability,
        level: int = logging.INFO,
    ) -> None:
        logger.log(
            level,
            "qa_observation %s",
            json.dumps(observation.model_dump(), sort_keys=True),
        )
