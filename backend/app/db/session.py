"""SQLAlchemy engine and session management."""

from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from ..config import Settings


def get_database_url(settings: Settings | None = None) -> str:
    """Return the configured database URL without logging or exposing it."""
    database_url = (settings or Settings.from_environment()).database_url
    if not database_url:
        raise RuntimeError(
            "DATABASE_URL is required for database operations. "
            "Set it in the local environment or backend/.env."
        )
    return database_url


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    """Create the process-wide SQLAlchemy engine on first database use."""
    return create_engine(get_database_url(), pool_pre_ping=True)


@lru_cache(maxsize=1)
def get_session_factory() -> sessionmaker[Session]:
    """Create the process-wide session factory on first database use."""
    return sessionmaker(bind=get_engine(), autoflush=False)


def get_session() -> Generator[Session, None, None]:
    """Yield a session for an application request and always close it."""
    with get_session_factory()() as session:
        yield session
