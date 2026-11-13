import uuid

from sqlalchemy import ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base, TimestampMixin, UUIDPKMixin, enum_col
from app.models.enums import ProcessingStatus


class Document(UUIDPKMixin, TimestampMixin, Base):
    """A user's private upload. Never public, never part of the Official Case Library."""

    __tablename__ = "documents"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)  # original, display only
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)  # internal, never returned
    file_type: Mapped[str] = mapped_column(String(10), nullable=False)  # pdf / txt / docx
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    processing_status: Mapped[ProcessingStatus] = mapped_column(
        enum_col(ProcessingStatus), default=ProcessingStatus.pending, nullable=False
    )
    extracted_text: Mapped[str | None] = mapped_column(Text)
    error_message: Mapped[str | None] = mapped_column(Text)
