import enum


class UserRole(str, enum.Enum):
    student = "student"
    reviewer = "reviewer"  # academic reviewer who may validate cases
    admin = "admin"


class ValidationStatus(str, enum.Enum):
    """Academic validation of content. Infrastructure being ready is NOT validated coverage."""

    not_started = "not_started"
    in_progress = "in_progress"
    validated = "validated"


class CaseType(str, enum.Enum):
    discovery = "discovery"
    revision = "revision"


class CaseStatus(str, enum.Enum):
    draft = "draft"
    validated = "validated"
    published = "published"
    archived = "archived"


class CaseSourceType(str, enum.Enum):
    authentic = "authentic"  # source-based
    simulated = "simulated"  # simulated educational scenario
    ai_draft = "ai_draft"  # AI-generated, must be reviewed before use


class SessionStatus(str, enum.Enum):
    in_progress = "in_progress"
    submitted = "submitted"
    completed = "completed"
    abandoned = "abandoned"


class MistakeType(str, enum.Enum):
    recall_failure = "recall_failure"
    conceptual_confusion = "conceptual_confusion"
    incorrect_relationship = "incorrect_relationship"
    application_error = "application_error"
    calculation_error = "calculation_error"
    elimination_error = "elimination_error"
    misinterpretation = "misinterpretation_of_question"
    guessing = "guessing"
    overthinking = "overthinking"


class ImprovementStatus(str, enum.Enum):
    new = "new"
    reviewing = "reviewing"
    improving = "improving"
    resolved = "resolved"


class ProcessingStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class MasteryStatus(str, enum.Enum):
    not_started = "not_started"
    learning = "learning"
    practising = "practising"
    proficient = "proficient"
    mastered = "mastered"


class RetentionStatus(str, enum.Enum):
    unknown = "unknown"
    fragile = "fragile"
    stable = "stable"
    strong = "strong"
