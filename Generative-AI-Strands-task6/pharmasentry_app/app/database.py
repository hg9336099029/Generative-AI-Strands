"""
Database setup.

In local-stub mode (PHARMASENTRY_LOCAL_STUB=true) we use SQLite via aiosqlite
so the backend is runnable without a live PostgreSQL instance.  The sync engine
(used only by the auth router / get_session) also switches to SQLite in that
mode.  Production always uses PostgreSQL via asyncpg.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

if settings.local_stub:
    # SQLite — no Postgres needed for local dev
    SQLALCHEMY_DATABASE_URL = "sqlite:///./pharmasentry_local.db"
    ASYNC_DATABASE_URL = "sqlite+aiosqlite:///./pharmasentry_local.db"
    _connect_args = {"check_same_thread": False}
else:
    SQLALCHEMY_DATABASE_URL = (
        f"postgresql://{settings.database_username}:{settings.database_password}"
        f"@{settings.database_hostname}:{settings.database_port}/{settings.database_name}"
    )
    ASYNC_DATABASE_URL = (
        f"postgresql+asyncpg://{settings.database_username}:{settings.database_password}"
        f"@{settings.database_hostname}:{settings.database_port}/{settings.database_name}"
    )
    _connect_args = {}

# Async database setup
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=False,
    future=True,
    connect_args=_connect_args,
)
async_session_maker = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Sync database setup (used by auth router's get_session)
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=_connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_session():
    """Synchronous database session dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_db():
    """Asynchronous database session dependency"""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()