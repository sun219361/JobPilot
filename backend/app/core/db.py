from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase

from app.core.config import settings


engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    echo=settings.debug,
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    class_=Session,
)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI dependency: DB 세션 주입"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
