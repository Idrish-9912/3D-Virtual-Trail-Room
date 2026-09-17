"""SQLAlchemy engine, session factory, and declarative Base.

A single ``SessionLocal`` dependency is exposed for FastAPI routes via
``get_db``. All models inherit from ``Base`` so Alembic can autogenerate
migrations from a single import of ``app.database.models``.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

# ``pool_pre_ping`` avoids stale-connection errors after DB restarts.
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    future=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI dependency that yields a scoped session and closes it after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
