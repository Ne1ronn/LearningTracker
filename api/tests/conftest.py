import uuid

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from dotenv import load_dotenv

from api.auth.functions import get_password_hash
from database.setup import get_session
from models import UserModel

load_dotenv()
from sqlalchemy import select, NullPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
import os

from main import app

DATABASE_URL_TEST = os.getenv("DATABASE_URL_TEST")
engine = create_async_engine(
    str(DATABASE_URL_TEST),
    echo=False,
    poolclass=NullPool
)

new_session = async_sessionmaker(engine, expire_on_commit=False)

async def override_get_session():
    async with new_session() as session:
        yield session

@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        app.dependency_overrides[get_session] = override_get_session
        yield ac
        app.dependency_overrides.pop(get_session, None)

@pytest.fixture
def user_payload():
    suffix = uuid.uuid4().hex[:8]
    return {
        "username": f"test_user_{suffix}",
        "email": f"test_{suffix}@example.com",
        "password": "test_password"
    }

@pytest.fixture
def entry_payload():
    suffix = uuid.uuid4().hex[:8]
    return {
        "title": f"Day-{suffix}",
        "description": "Learned SQLAlchemy",
        "tags": f"python,sqlalchemy, {suffix}",
        "mood_score": 8,
        "progress_score": 7,
        "learning_hours": 2.5,
        "private": False,
        "topic_ids": []
    }

@pytest_asyncio.fixture
async def admin_headers(client):
    async with new_session() as session:
        result = await session.execute(
            select(UserModel).where(UserModel.username == "test_admin")
        )
        admin = result.scalar_one_or_none()

        if admin is None:
            admin = UserModel(
                username="test_admin",
                email="test_admin@example.com",
                hashed_password=get_password_hash("test_password"),
                role="admin",
            )
            session.add(admin)
            await session.commit()

    login = await client.post(
        "/login",
        data={"username": "test_admin", "password": "test_password"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}