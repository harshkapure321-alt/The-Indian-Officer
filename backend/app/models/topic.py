import uuid

from sqlalchemy import ForeignKey, Index, Integer, String, Text, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base, JSONType, TimestampMixin, UUIDPKMixin, enum_col
from app.models.enums import ValidationStatus


class Topic(UUIDPKMixin, TimestampMixin, Base):
    """Topics and subtopics share one self-referencing table.

    parent_topic_id IS NULL  -> top-level topic
    parent_topic_id NOT NULL -> subtopic (can nest further if ever needed)
    """

    __tablename__ = "topics"
    __table_args__ = (
        UniqueConstraint("subject_id", "parent_topic_id", "name", name="uq_topic_name_per_parent"),
        Index("ix_topics_subject_parent_seq", "subject_id", "parent_topic_id", "sequence_number"),
    )

    subject_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False
    )
    parent_topic_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("topics.id", ondelete="CASCADE")
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    syllabus_mapping: Mapped[str | None] = mapped_column(Text)
    sequence_number: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    exam_relevance: Mapped[str | None] = mapped_column(Text)
    learning_objectives: Mapped[list] = mapped_column(JSONType, default=list, nullable=False)
    academic_references: Mapped[list] = mapped_column(JSONType, default=list, nullable=False)
    validation_status: Mapped[ValidationStatus] = mapped_column(
        enum_col(ValidationStatus), default=ValidationStatus.not_started, nullable=False
    )


class Concept(UUIDPKMixin, TimestampMixin, Base):
    """A mappable unit of knowledge (e.g. 'Local mean solar time'). Used for mistakes and mastery."""

    __tablename__ = "concepts"
    __table_args__ = (UniqueConstraint("topic_id", "name", name="uq_concept_name_per_topic"),)

    topic_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("topics.id", ondelete="CASCADE"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    related_concept_ids: Mapped[list] = mapped_column(JSONType, default=list, nullable=False)
