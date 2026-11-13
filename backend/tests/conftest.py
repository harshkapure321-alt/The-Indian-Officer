import os

# Force test settings BEFORE the app is imported, so a real .env can never point tests at a real DB.
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SECRET_KEY"] = "test-secret-key-for-pytest-only-1234567890"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

import app.models  # noqa: E402,F401
from app.database.base import Base  # noqa: E402
from app.database.session import get_db  # noqa: E402
from app.main import app  # noqa: E402

PASSWORD = "Passw0rd123"


@pytest.fixture()
def db_session_factory():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    yield sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture()
def db(db_session_factory):
    session = db_session_factory()
    yield session
    session.close()


@pytest.fixture()
def client(db_session_factory):
    def override_get_db():
        session = db_session_factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def register_user(client, email="asha@example.com", name="Asha", password=PASSWORD):
    return client.post(
        "/api/v1/auth/register", json={"name": name, "email": email, "password": password}
    )


def login_headers(client, email="asha@example.com", password=PASSWORD) -> dict:
    """Register (if needed) and log in; returns Authorization headers."""
    register_user(client, email=email, password=password)
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    token = resp.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}
