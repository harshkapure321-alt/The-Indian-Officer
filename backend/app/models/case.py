import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base, JSONType, TimestampMixin, UUIDPKMixin, enum_col
from app.models.enums import CaseSourceType, CaseStatus, CaseType


class Case(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "cases"
    __table_args__ = (
        Index("ix_cases_subject_topic", "subject_id", "topic_id"),
        Index("ix_cases_status_type", "status", "case_type"),
    )

    case_code: Mapped[str] = mapped_column(String(40), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    case_type: Mapped[CaseType] = mapped_column(enum_col(CaseType), nullable=False)
    subject_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("subjects.id", ondelete="RESTRICT"), nullable=False
    )
    topic_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("topics.id", ondelete="RESTRICT"), nullable=False
    )
    subtopic_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("topics.id", ondelete="SET NULL")
    )
    difficulty_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)  # 1-5
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    learning_objectives: Mapped[list] = mapped_column(JSONType, default=list, nullable=False)
    estimated_duration: Mapped[int | None] = mapped_column(Integer)  # minutes

    # Data-driven case: stages/questions live here, not in Python code.
    case_content: Mapped[dict] = mapped_column(JSONType, default=dict, nullable=False)
    # NEVER returned by public schemas. Server-side evaluation only.
    answer_key: Mapped[dict] = mapped_column(JSONType, default=dict, nullable=False)
    evaluation_rubric: Mapped[dict] = mapped_column(JSONType, default=dict, nullable=False)

    status: Mapped[CaseStatus] = mapped_column(
        enum_col(CaseStatus), default=CaseStatus.draft, nullable=False
    )
    source_type: Mapped[CaseSourceType] = mapped_column(
        enum_col(CaseSourceType), default=CaseSourceType.simulated, nullable=False
    )
    source_references: Mapped[list] = mapped_column(JSONType, default=list, nullable=False)
    validated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    validated_by: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="SET NULL")
    )
    # Set when a case was generated from a user's private document; keeps it out of the library.
    owner_user_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
