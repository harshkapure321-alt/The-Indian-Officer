"""Seed the Geography subject and its 9 working learning categories.

Run:  python -m app.utils.seed_geography      (safe to run repeatedly)

IMPORTANT: this seeds *infrastructure* only. Every topic is marked `not_started` for academic
validation. No syllabus references or PYQ references are invented here; add only verified ones.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import ValidationStatus
from app.models.subject import Subject
from app.models.topic import Topic

GEOGRAPHY_CATEGORIES = [
    "Geographical Foundations",
    "Earth and Its Fundamentals",
    "Cartography and Map Skills",
    "Geospatial Technology",
    "Physical Geography",
    "Indian Geography",
    "World Geography",
    "Human and Economic Geography",
    "Applied Geography and Natural Hazards",
]

CATEGORY_NOTE = (
    "Expanded learning category, not a verbatim UPSC syllabus heading. "
    "Academic validation of content has not started."
)


def seed_geography(db: Session) -> Subject:
    subject = db.scalar(select(Subject).where(Subject.name == "Geography"))
    if subject is None:
        subject = Subject(
            name="Geography",
            exam_category="UPSC Prelims",
            description="Investigation-based Geography learning environment.",
            syllabus_reference=None,
            coverage_status=ValidationStatus.not_started,
        )
        db.add(subject)
        db.flush()

    for index, name in enumerate(GEOGRAPHY_CATEGORIES, start=1):
        exists = db.scalar(
            select(Topic).where(
                Topic.subject_id == subject.id,
                Topic.parent_topic_id.is_(None),
                Topic.name == name,
            )
        )
        if exists is None:
            db.add(
                Topic(
                    subject_id=subject.id,
                    name=name,
                    description=CATEGORY_NOTE,
                    sequence_number=index,
                    validation_status=ValidationStatus.not_started,
                )
            )
    db.commit()
    return subject


if __name__ == "__main__":
    from app.database.session import SessionLocal

    with SessionLocal() as session:
        seeded = seed_geography(session)
        print(f"Seeded subject: {seeded.name} ({len(GEOGRAPHY_CATEGORIES)} categories)")
