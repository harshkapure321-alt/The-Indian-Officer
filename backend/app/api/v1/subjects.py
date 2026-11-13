import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.session import get_db
from app.models.subject import Subject
from app.models.topic import Topic
from app.models.user import User
from app.schemas.common import Envelope
from app.schemas.subject import SubjectOut, TopicNode

router = APIRouter(tags=["Subjects"])


def _get_active_subject(db: Session, subject_id: uuid.UUID) -> Subject:
    subject = db.get(Subject, subject_id)
    if subject is None or not subject.is_active:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Subject not found")
    return subject


@router.get("/subjects", response_model=Envelope[list[SubjectOut]])
def list_subjects(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    rows = db.scalars(select(Subject).where(Subject.is_active.is_(True)).order_by(Subject.name))
    return Envelope(data=[SubjectOut.model_validate(r) for r in rows])


@router.get("/subjects/{subject_id}", response_model=Envelope[SubjectOut])
def get_subject(
    subject_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)
):
    return Envelope(data=SubjectOut.model_validate(_get_active_subject(db, subject_id)))


@router.get("/subjects/{subject_id}/topics", response_model=Envelope[list[TopicNode]])
def list_subject_topics(
    subject_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)
):
    """Return the subject's full topic -> subtopic tree, ordered by sequence_number."""
    _get_active_subject(db, subject_id)
    topics = db.scalars(
        select(Topic).where(Topic.subject_id == subject_id).order_by(Topic.sequence_number, Topic.name)
    ).all()

    nodes = {t.id: TopicNode.model_validate(t) for t in topics}
    roots: list[TopicNode] = []
    for t in topics:  # already sorted, so children stay in order
        node = nodes[t.id]
        parent = nodes.get(t.parent_topic_id) if t.parent_topic_id else None
        (parent.children if parent else roots).append(node)
    return Envelope(data=roots)
