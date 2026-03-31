"""
MHRS SaaS — Database Engine & Session Factory
SQLAlchemy synchronous setup with MariaDB via pymysql.
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from typing import Generator
from app.config import get_settings

settings = get_settings()

# ── Engine ────────────────────────────────────────────────────────────────────
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,          # Reconnect on stale connections
    pool_size=10,                # Connection pool size
    max_overflow=20,             # Extra connections above pool_size
    pool_recycle=3600,           # Recycle connections after 1 hour
    echo=settings.debug,         # Log SQL in development
)

# ── Session Factory ───────────────────────────────────────────────────────────
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# ── Base Class for all ORM models ─────────────────────────────────────────────
class Base(DeclarativeBase):
    pass


# ── FastAPI Dependency ────────────────────────────────────────────────────────
def get_db() -> Generator:
    """
    Provides a database session for each request.
    Automatically closes the session after the request completes.

    Usage:
        @router.get("/example")
        def example(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_all_tables() -> None:
    """Creates all tables defined in ORM models. Called on app startup."""
    from app.models import user, doctor, clinic, appointment  # noqa: F401
    Base.metadata.create_all(bind=engine)


def check_db_connection() -> bool:
    """Health check — verifies MariaDB is reachable."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
