"""Response tables live in investigation.py (they are tightly coupled to sessions).

This module re-exports them so the layout in the assignment's recommended structure still works.
"""

from app.models.investigation import HintHistory, InvestigationResponse  # noqa: F401
