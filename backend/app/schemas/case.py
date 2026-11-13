import uuid

from pydantic import BaseModel, ConfigDict

from app.models.enums import CaseSourceType, CaseStatus, CaseType


class CaseSummary(BaseModel):
    """Public case listing. Intentionally excludes answer_key, evaluation_rubric and case_content."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    case_code: str
    title: str
    case_type: CaseType
    subject_id: uuid.UUID
    topic_id: uuid.UUID
    subtopic_id: uuid.UUID | None
    difficulty_level: int
    description: str
    learning_objectives: list
    estimated_duration: int | None
    source_type: CaseSourceType
    source_references: list
    status: CaseStatus
