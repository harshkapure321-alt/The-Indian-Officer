import uuid

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ValidationStatus


class SubjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    exam_category: str
    description: str | None
    syllabus_reference: str | None
    coverage_status: ValidationStatus


class TopicOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    subject_id: uuid.UUID
    parent_topic_id: uuid.UUID | None
    name: str
    description: str | None
    syllabus_mapping: str | None
    sequence_number: int
    exam_relevance: str | None
    learning_objectives: list
    academic_references: list
    validation_status: ValidationStatus


class TopicNode(TopicOut):
    """Topic with its nested subtopics (used for the subject hierarchy)."""

    children: list["TopicNode"] = Field(default_factory=list)


class TopicDetail(TopicOut):
    subtopics: list[TopicOut] = Field(default_factory=list)
