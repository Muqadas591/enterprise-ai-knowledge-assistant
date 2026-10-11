from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.api.deps import get_db
from app.models.user import User
from app.schemas.feedback import (
    FeedbackCreate,
    FeedbackResponse,
)
from app.services.message_feedback_service import (
    MessageFeedbackService,
)
from app.schemas.feedback_analytics import (
    FeedbackAnalyticsResponse,
)

router = APIRouter(
    prefix="/feedback",
    tags=["Feedback"],
)


@router.post(
    "/messages/{message_id}",
    response_model=FeedbackResponse,
)
def submit_message_feedback(
    message_id: int,
    request: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = MessageFeedbackService(db)

    feedback = service.submit_feedback(
        message_id=message_id,
        user_id=current_user.id,
        rating=request.rating,
        comment=request.comment,
    )

    return feedback
@router.get(
    "/analytics",
    response_model=FeedbackAnalyticsResponse,
)
async def feedback_analytics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = MessageFeedbackService(db)

    return await service.get_analytics(
        user_id=str(current_user.id)
    )