"""
MHRS SaaS — PyTest Configuration & Fixtures
Uses in-memory SQLite for fast, Docker-free testing.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, MagicMock

from app.main import create_app
from app.database import Base, get_db

# ── In-memory SQLite engine for tests ────────────────────────────────────────
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Creates all tables in the test DB once per session."""
    # Import all models to register them
    from app.models import user, doctor, clinic, appointment  # noqa
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture()
def db():
    """Provides a clean DB session per test with rollback."""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db):
    """FastAPI TestClient with DB override and mocked external services."""
    app = create_app()
    app.dependency_overrides[get_db] = lambda: db

    # Mock RabbitMQ publish so tests don't need a broker
    with patch("app.routers.auth.publish_email_verification", return_value=None):
        with TestClient(app, raise_server_exceptions=True) as c:
            yield c


@pytest.fixture()
def registered_user(client):
    """Registers and verifies a test user, returns their data."""
    reg_resp = client.post("/api/v1/auth/register", json={
        "tc_no": "12345678901",
        "name": "Test User",
        "email": "test@example.com",
        "password": "TestPass123",
    })
    assert reg_resp.status_code == 201

    # Manually verify via DB (bypass email)
    from app.models.user import User
    session = TestingSessionLocal()
    user = session.query(User).filter_by(email="test@example.com").first()
    user.is_verified = True
    user.verification_code = None
    session.commit()
    session.close()

    return {"email": "test@example.com", "password": "TestPass123"}


@pytest.fixture()
def auth_headers(client, registered_user):
    """Returns Authorization headers for an authenticated test user."""
    resp = client.post("/api/v1/auth/login", json=registered_user)
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
