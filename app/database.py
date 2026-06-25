"""Database setup — async SQLite via SQLAlchemy."""

import os

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


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    async with async_session() as session:
        yield session
