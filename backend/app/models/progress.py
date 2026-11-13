import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base, TimestampMixin, UUIDPKMixin, enum_col
from app.models.enums import MasteryStatus, RetentionStatus


class UserProgress(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "user_progress"
    __table_args__ = (UniqueConstraint("user_id", "topic_id", name="uq_progress_user_topic"),)

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    subject_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("subjects.id", ondelete="CASCADE"), index=True, nullable=False
    )
    topic_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("topics.id", ondelete="CASCADE"), nullable=False
    )
    cases_attempted: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cases_completed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    average_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    last_activity: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    mastery_status: Mapped[MasteryStatus] = mapped_column(
        enum_col(MasteryStatus), default=MasteryStatus.not_started, nullable=False
    )


class ConceptMastery(UUIDPKMixin, TimestampMixin, Base):
    """Per-concept mastery across the five revision abilities. Scores are 0.0 - 1.0."""

    __tablename__ = "concept_mastery"
    __table_args__ = (UniqueConstraint("user_id", "concept_id", name="uq_mastery_user_concept"),)

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    concept_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False
    )
    retrieval_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    reconstruction_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    connection_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    application_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    elimination_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    confidence_accuracy: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    retention_status: Mapped[RetentionStatus] = mapped_column(
        enum_col(RetentionStatus), default=RetentionStatus.unknown, nullable=False
    )
    last_reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
