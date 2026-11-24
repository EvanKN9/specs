"""Database connectivity checks."""

from sqlalchemy import Engine, text
from sqlalchemy.exc import SQLAlchemyError


def check_database_connection(engine: Engine) -> bool:
    """Return whether the database accepts a simple read-only query."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except SQLAlchemyError:
        return False
