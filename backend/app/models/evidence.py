import uuid

from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base, JSONType, TimestampMixin, UUIDPKMixin


class Evidence(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "evidence"
    __table_args__ = (UniqueConstraint("case_id", "sequence_number", name="uq_evidence_seq"),)

    case_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("cases.id", ondelete="CASCADE"), index=True, nullable=False
    )
    # image / map / data_table / document / coordinates / chart / report / numeric / interactive
    evidence_type: Mapped[str] = mapped_column(String(40), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    content: Mapped[dict] = mapped_column(JSONType, default=dict, nullable=False)
    file_path: Mapped[str | None] = mapped_column(String(500))
    sequence_number: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    # Column is named "metadata"; the attribute can't be, because Base.metadata is reserved.
    meta: Mapped[dict] = mapped_column("metadata", JSONType, default=dict, nullable=False)
