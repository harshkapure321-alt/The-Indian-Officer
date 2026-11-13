import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base, JSONType, TimestampMixin, UUIDPKMixin, enum_col
from app.models.enums import SessionStatus


class InvestigationSession(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "investigation_sessions"
    __table_args__ = (Index("ix_sessions_user_case", "user_id", "case_id"),)

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    case_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("cases.id", ondelete="RESTRICT"), index=True, nullable=False
    )
    status: Mapped[SessionStatus] = mapped_column(
        enum_col(SessionStatus), default=SessionStatus.in_progress, nullable=False
    )
    current_stage: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    confidence_level: Mapped[int | None] = mapped_column(Integer)  # self-reported, 1-5
    hints_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    final_score: Mapped[float | None] = mapped_column(Float)
    evaluation_summary: Mapped[dict | None] = mapped_column(JSONType)  # structured result


class InvestigationResponse(UUIDPKMixin, Base):
    """Every submitted answer is kept, including wrong ones (history is never overwritten)."""

    __tablename__ = "investigation_responses"
    __table_args__ = (Index("ix_responses_session_stage", "session_id", "stage_number"),)

    session_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("investigation_sessions.id", ondelete="CASCADE"), nullable=False
    )
    stage_number: Mapped[int] = mapped_column(Integer, nullable=False)
    question_id: Mapped[str] = mapped_column(String(80), nullable=False)
    response_kind: Mapped[str] = mapped_column(
        String(30), default="answer", nullable=False
    )  # answer / observation / hypothesis / explanation
    attempt_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    user_response: Mapped[dict] = mapped_column(JSONType, nullable=False)
    confidence: Mapped[int | None] = mapped_column(Integer)  # 1-5 for this answer
    is_correct: Mapped[bool | None] = mapped_column()
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    evaluation_result: Mapped[dict | None] = mapped_column(JSONType)
    feedback: Mapped[str | None] = mapped_column(Text)


class HintHistory(UUIDPKMixin, Base):
    __tablename__ = "hint_history"
    __table_args__ = (Index("ix_hints_session_stage", "session_id", "stage_number"),)

    session_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("investigation_sessions.id", ondelete="CASCADE"), nullable=False
    )
    stage_number: Mapped[int] = mapped_column(Integer, nullable=False)
    hint_level: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-4 (0 = no help)
    hint_content: Mapped[str] = mapped_column(Text, nullable=False)
    # "rule_based" vs "ai" so genuine AI output is never confused with predefined hints
    source: Mapped[str] = mapped_column(String(20), default="rule_based", nullable=False)
    requested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
