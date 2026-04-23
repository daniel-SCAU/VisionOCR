import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import Settings

logger = logging.getLogger(__name__)

Base = declarative_base()

_engine = None
_SessionLocal = None


def get_engine(settings: Settings | None = None):
    global _engine
    if _engine is None:
        if settings is None:
            settings = Settings()
        connect_args = {}
        if "sqlite" in settings.DATABASE_URL:
            connect_args = {"check_same_thread": False}
        _engine = create_engine(
            settings.DATABASE_URL,
            connect_args=connect_args,
        )
    return _engine


def get_session_local(settings: Settings | None = None):
    global _SessionLocal
    if _SessionLocal is None:
        engine = get_engine(settings)
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return _SessionLocal


def get_db():
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db(settings: Settings | None = None) -> None:
    from app import models  # noqa: F401
    engine = get_engine(settings)
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized.")
