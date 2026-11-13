from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base, TimestampMixin, UUIDPKMixin, enum_col
from app.models.enums import ValidationStatus


class Subject(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "subjects"

    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    exam_category: Mapped[str] = mapped_column(String(80), nullable=False)  # e.g. "UPSC Prelims"
    description: Mapped[str | None] = mapped_column(Text)
    syllabus_reference: Mapped[str | None] = mapped_column(Text)  # only verified references
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    # Separates "subject works technically" from "syllabus actually validated".
    coverage_status: Mapped[ValidationStatus] = mapped_column(
        enum_col(ValidationStatus), default=ValidationStatus.not_started, nullable=False
    )
