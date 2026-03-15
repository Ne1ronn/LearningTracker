import uuid
import pytest
import os
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from ..crud.auth.auth_service import get_password_hash
from database.setup import get_session
from models import UserModel
from sqlalchemy import select, NullPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from main import app

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL_TEST = os.getenv("DATABASE_URL_TEST")
engine = create_async_engine(str(DATABASE_URL_TEST), echo=False, poolclass=NullPool)

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
        "password": "test_password",
    }


@pytest_asyncio.fixture()
async def user_headers(client):
    suffix = uuid.uuid4().hex[:8]
    user_payload = {
        "username": f"test_user_{suffix}",
        "email": f"test_{suffix}@example.com",
        "password": "test_password",
    }

    await client.post("/register", json=user_payload)

    login = await client.post(
        "/login",
        data={
            "username": user_payload["username"],
            "password": user_payload["password"],
        },
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    return headers


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
        "topic_ids": [],
    }
