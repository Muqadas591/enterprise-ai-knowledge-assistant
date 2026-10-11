import asyncio
import json
import logging
import time
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import StreamingResponse
from openai import RateLimitError
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.api.deps import get_db
from app.core.config import settings
from app.llm.factory import get_llm_service
from app.models.message import Message
from app.models.user import User
from app.schemas.qa import QARequest, QAResponse, SourceCitation
from app.schemas.retrieval_filters import RetrievalFilters
from app.services.conversation_context import ConversationContextBuilder
from app.services.conversation_service import ConversationService
from app.services.hybrid_retrieval_service import HybridRetrievalService
from app.services.query_rewrite_service import QueryRewriteService
from app.services.rag_service import RAGService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/qa",
    tags=["Question Answering"],
)


@router.post(
    "/ask",
    response_model=QAResponse,
)
def ask_question(
    qa_request: QARequest,
    http_request: Request,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    request_id = getattr(http_request.state, "request_id", str(uuid4()))
    response.headers["X-Request-ID"] = request_id
    started = time.perf_counter()
    conversation_service = ConversationService(db)
    try:
        if qa_request.conversation_id is None:
            conversation = conversation_service.create_conversation(current_user.id)
        else:
            conversation = conversation_service.verify_ownership(
                qa_request.conversation_id,
                current_user.id,
            )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc

    history = ConversationContextBuilder().build(
        conversation_service.get_messages(conversation.id, limit=10),
    )
    try:
        llm_service = get_llm_service()
        rewritten_question = QueryRewriteService(llm_service).rewrite(
            question=qa_request.question,
            history=history,
        )
    except RateLimitError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The configured LLM provider has no remaining quota. Set LLM_PROVIDER=demo for local testing or restore provider credits.",
        ) from exc

    conversation_service.add_message(
        conversation_id=conversation.id,
        role="user",
        content=qa_request.question,
    )
    conversation = conversation_service.update_title_from_question(
        conversation,
        qa_request.question,
    )

    filters = RetrievalFilters(
        document_category=qa_request.document_category,
        document_type=qa_request.document_type,
        department=qa_request.department,
        document_id=qa_request.document_id,
    )

    try:
        rag_service = RAGService(
            retrieval_service=HybridRetrievalService(db),
            llm_service=llm_service,
        )
    except Exception as exc:
        logger.error(
            "qa_observation %s",
            json.dumps(
                {
                    "request_id": request_id,
                    "question": qa_request.question,
                    "retrieval_latency_ms": 0.0,
                    "llm_latency_ms": 0.0,
                    "total_latency_ms": (time.perf_counter() - started) * 1000,
                    "retrieved_chunks": 0,
                    "model": settings.LLM_MODEL,
                    "token_usage": None,
                    "citation_count": 0,
                    "status": "error",
                    "error": str(exc),
                },
                sort_keys=True,
            ),
        )
        raise
    try:
        result = rag_service.answer(
            question=qa_request.question,
            top_k=qa_request.top_k,
            filters=filters,
            request_id=request_id,
            retrieval_query=rewritten_question,
        )
    except RateLimitError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The configured LLM provider has no remaining quota. Set LLM_PROVIDER=demo for local testing or restore provider credits.",
        ) from exc

    assistant_message = conversation_service.add_message(
        conversation_id=conversation.id,
        role="assistant",
        content=result.answer,
        model=result.model,
    )

    return QAResponse(
        conversation_id=conversation.id,
        message_id=assistant_message.id,
        answer=result.answer,
        model=result.model,
        sources=[
            SourceCitation(
                source_id=source.source_id,
                document_id=source.document_id,
                filename=source.filename,
                chunk_id=source.chunk_id,
                chunk_index=source.chunk_index,
                page_number=source.page_number,
            )
            for source in result.sources
        ],
        quality=result.quality,
        observability=result.observability,
    )


@router.post("/ask/stream")
async def stream_answer(
    request: Request,
    qa_request: QARequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    request_id = getattr(request.state, "request_id", str(uuid4()))
    conversation_service = ConversationService(db)
    try:
        if qa_request.conversation_id is None:
            conversation = conversation_service.create_conversation(current_user.id)
        else:
            conversation = conversation_service.verify_ownership(
                qa_request.conversation_id,
                current_user.id,
            )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc

    if qa_request.regenerate_message_id is not None:
        regenerate_message = db.get(Message, qa_request.regenerate_message_id)
        if (
            regenerate_message is None
            or regenerate_message.conversation_id != conversation.id
            or regenerate_message.role != "assistant"
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assistant message not found.",
            )

    history = ConversationContextBuilder().build(
        conversation_service.get_messages(conversation.id, limit=10),
    )
    try:
        llm_service = get_llm_service()
        rewritten_question = QueryRewriteService(llm_service).rewrite(
            question=qa_request.question,
            history=history,
        )
    except RateLimitError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The configured LLM provider has no remaining quota.",
        ) from exc

    if not qa_request.regenerate:
        existing_messages = conversation_service.get_messages(
            conversation.id,
            limit=50,
        )
        last_message = existing_messages[-1] if existing_messages else None
        if not (
            last_message
            and last_message.role == "user"
            and last_message.content == qa_request.question
        ):
            conversation_service.add_message(
                conversation_id=conversation.id,
                role="user",
                content=qa_request.question,
            )
        conversation = conversation_service.update_title_from_question(
            conversation,
            qa_request.question,
        )

    filters = RetrievalFilters(
        document_category=qa_request.document_category,
        document_type=qa_request.document_type,
        department=qa_request.department,
        document_id=qa_request.document_id,
    )
    rag_service = RAGService(
        retrieval_service=HybridRetrievalService(db),
        llm_service=llm_service,
    )

    async def event_generator():
        full_answer = ""
        completed = False
        try:
            async for event in rag_service.stream_answer(
                question=qa_request.question,
                top_k=qa_request.top_k,
                filters=filters,
                request_id=request_id,
                retrieval_query=rewritten_question,
            ):
                if await request.is_disconnected():
                    break

                if event["type"] == "token":
                    full_answer += event["data"]["text"]
                elif event["type"] == "done":
                    completed = True
                    if completed and full_answer.strip():
                        if qa_request.regenerate_message_id is not None:
                            assistant_message = (
                                conversation_service.replace_assistant_message(
                                    message_id=qa_request.regenerate_message_id,
                                    conversation_id=conversation.id,
                                    content=full_answer,
                                    model=event["data"].get("model"),
                                )
                            )
                        else:
                            assistant_message = conversation_service.add_message(
                                conversation_id=conversation.id,
                                role="assistant",
                                content=full_answer,
                                model=event["data"].get("model"),
                            )
                        event["data"]["assistant_message_id"] = assistant_message.id
                        event["data"]["conversation_id"] = conversation.id
                        event["data"]["conversation_title"] = conversation.title

                yield f"data: {json.dumps(event)}\n\n"
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Streaming QA failed for request %s", request_id)
            payload = {
                "type": "error",
                "data": {
                    "message": (
                        "The AI service could not complete your request."
                    ),
                },
            }
            yield f"data: {json.dumps(payload)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "X-Request-ID": request_id,
        },
    )
