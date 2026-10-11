"""Database setup — async SQLite via SQLAlchemy."""

import os

from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

_raw_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./wfa.db")
# Render provides postgres:// or postgresql:// but asyncpg requires postgresql+asyncpg://
if _raw_url.startswith("postgresql://"):
    _raw_url = "postgresql+asyncpg://" + _raw_url[len("postgresql://"):]
elif _raw_url.startswith("postgres://"):
    _raw_url = "postgresql+asyncpg://" + _raw_url[len("postgres://"):]
DATABASE_URL = _raw_url

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


# create_all() only creates missing tables; it never alters existing ones. Columns
# added to a model after its table already exists in a deployed database must be
# listed here so startup adds them. (table, column, SQL type)
_ADDED_COLUMNS = [
    ("users", "reset_token", "VARCHAR(255)"),
    ("users", "reset_token_expires", "TIMESTAMP"),
]
_ADDED_INDEXES = [
    "CREATE INDEX IF NOT EXISTS ix_users_reset_token ON users (reset_token)",
]


def _add_missing_columns(sync_conn):
    insp = inspect(sync_conn)
    for table, column, sql_type in _ADDED_COLUMNS:
        existing = {c["name"] for c in insp.get_columns(table)}
        if column not in existing:
            sync_conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {sql_type}"))
    for stmt in _ADDED_INDEXES:
        sync_conn.execute(text(stmt))


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(_add_missing_columns)


async def get_db():
    async with async_session() as session:
        yield session
