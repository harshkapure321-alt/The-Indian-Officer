"""Import every model so Base.metadata is complete (needed by Alembic and tests)."""

from app.models.case import Case  # noqa: F401
from app.models.document import Document  # noqa: F401
from app.models.evidence import Evidence  # noqa: F401
from app.models.investigation import (  # noqa: F401
    HintHistory,
    InvestigationResponse,
    InvestigationSession,
)
from app.models.mistake import MistakeNotebook  # noqa: F401
from app.models.progress import ConceptMastery, UserProgress  # noqa: F401
from app.models.subject import Subject  # noqa: F401
from app.models.topic import Concept, Topic  # noqa: F401
from app.models.user import User  # noqa: F401
