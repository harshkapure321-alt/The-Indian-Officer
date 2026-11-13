import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.session import get_db
from app.models.case import Case
from app.models.enums import CaseStatus, CaseType
from app.models.topic import Topic
from app.models.user import User
from app.schemas.case import CaseSummary
from app.schemas.common import Envelope
from app.schemas.subject import TopicDetail, TopicOut

router = APIRouter(tags=["Topics"])


def _get_topic(db: Session, topic_id: uuid.UUID) -> Topic:
    topic = db.get(Topic, topic_id)
    if topic is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Topic not found")
    return topic


@router.get("/topics/{topic_id}", response_model=Envelope[TopicDetail])
def get_topic(topic_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    topic = _get_topic(db, topic_id)
    subtopics = db.scalars(
        select(Topic).where(Topic.parent_topic_id == topic_id).order_by(Topic.sequence_number)
    ).all()
    detail = TopicDetail.model_validate(topic)
    detail.subtopics = [TopicOut.model_validate(s) for s in subtopics]
    return Envelope(data=detail)


@router.get("/topics/{topic_id}/cases", response_model=Envelope[list[CaseSummary]])
def list_topic_cases(
    topic_id: uuid.UUID,
    case_type: CaseType | None = Query(default=None),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Published, library-level cases for a topic. Answer keys are never included."""
    _get_topic(db, topic_id)
    stmt = (
        select(Case)
        .where(
            or_(Case.topic_id == topic_id, Case.subtopic_id == topic_id),
            Case.status == CaseStatus.published,
            Case.owner_user_id.is_(None),  # private, document-generated cases stay private
        )
        .order_by(Case.difficulty_level, Case.case_code)
    )
    if case_type is not None:
        stmt = stmt.where(Case.case_type == case_type)
    return Envelope(data=[CaseSummary.model_validate(c) for c in db.scalars(stmt)])
