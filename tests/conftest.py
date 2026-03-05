"""Shared test fixtures — in-memory DB, async client, user helpers."""

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.auth import create_token, hash_password
from app.database import Base, get_db
from app.models.user import User

# Import all models so Base.metadata knows every table.
from app.models import chat, complaint, compliance, user as _user_mod  # noqa: F401


@pytest.fixture
async def test_engine():
    engine = create_async_engine("sqlite+aiosqlite://", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def db_session(test_engine):
    TestSession = sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
    async with TestSession() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def client(test_engine):
    """httpx AsyncClient wired to the FastAPI app with an in-memory DB."""
    TestSession = sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

    async def _override_get_db():
        async with TestSession() as session:
            yield session

    # Import app here so module-level side-effects don't fire too early.
    from app.main import app

    app.dependency_overrides[get_db] = _override_get_db
    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# User helpers
# ---------------------------------------------------------------------------

async def create_test_user(
    db: AsyncSession,
    *,
    email: str = "test@example.com",
    password: str = "password123",
    full_name: str = "Test User",
    role: str = "employee",
    country: str = "us",
    is_subscribed: bool = False,
) -> User:
    user = User(
        email=email,
        full_name=full_name,
        hashed_password=hash_password(password),
        role=role,
        country=country,
        is_subscribed=is_subscribed,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest.fixture
async def test_user(db_session):
    return await create_test_user(db_session)


@pytest.fixture
async def subscribed_user(db_session):
    return await create_test_user(
        db_session, email="pro@example.com", full_name="Pro User", is_subscribed=True
    )


@pytest.fixture
async def employer_user(db_session):
    return await create_test_user(
        db_session,
        email="employer@example.com",
        full_name="Employer User",
        role="employer",
    )


def _auth_cookies(user: User) -> dict[str, str]:
    token = create_token(user.id, user.email)
    return {"access_token": token}


@pytest.fixture
async def auth_client(test_engine, test_user):
    """Client with a regular (free) user session."""
    TestSession = sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

    async def _override():
        async with TestSession() as s:
            yield s

    from app.main import app

    app.dependency_overrides[get_db] = _override
    transport = ASGITransport(app=app, raise_app_exceptions=False)
    cookies = _auth_cookies(test_user)
    async with AsyncClient(transport=transport, base_url="http://test", cookies=cookies) as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
async def subscribed_client(test_engine, subscribed_user):
    """Client with a subscribed user session."""
    TestSession = sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

    async def _override():
        async with TestSession() as s:
            yield s

    from app.main import app

    app.dependency_overrides[get_db] = _override
    transport = ASGITransport(app=app, raise_app_exceptions=False)
    cookies = _auth_cookies(subscribed_user)
    async with AsyncClient(transport=transport, base_url="http://test", cookies=cookies) as ac:
        yield ac
    app.dependency_overrides.clear()
