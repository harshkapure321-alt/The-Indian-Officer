from collections.abc import Iterator

from sqlalchemy.orm import Session, sessionmaker

from app.database.connection import engine

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
