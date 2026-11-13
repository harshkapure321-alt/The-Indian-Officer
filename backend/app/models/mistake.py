import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base, JSONType, TimestampMixin, UUIDPKMixin, enum_col
from app.models.enums import ImprovementStatus, MistakeType


class MistakeNotebook(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "mistake_notebook"
    __table_args__ = (
        Index("ix_mistakes_user_type", "user_id", "mistake_type"),
        Index("ix_mistakes_user_next_review", "user_id", "next_review_at"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    session_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("investigation_sessions.id", ondelete="SET NULL"), index=True
    )
    concept_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("concepts.id", ondelete="SET NULL"), index=True
    )
    mistake_type: Mapped[MistakeType] = mapped_column(enum_col(MistakeType), nullable=False)
    original_response: Mapped[dict] = mapped_column(JSONType, nullable=False)
    correct_understanding: Mapped[str] = mapped_column(Text, nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)  # why the response was wrong
    relevant_evidence: Mapped[list] = mapped_column(JSONType, default=list, nullable=False)
    recommended_revision: Mapped[str | None] = mapped_column(Text)
    improvement_status: Mapped[ImprovementStatus] = mapped_column(
        enum_col(ImprovementStatus), default=ImprovementStatus.new, nullable=False
    )
    occurrence_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    next_review_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
