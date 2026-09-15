from fastapi import APIRouter

from app.schemas.common import MessageResponse

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


@router.get(
    "",
    response_model=MessageResponse,
)
def list_documents() -> MessageResponse:
    return MessageResponse(
        message="Document API initialized.",
    )