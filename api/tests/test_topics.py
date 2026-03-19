import pytest


async def create_topic_and_get_id(client, headers):
    topic_payload = {
        "title": "FastAPI",
        "skill": "Backend Development",
        "description": "Python async backend framework",
        "category": "Frameworks",
        "is_active": True,
    }

    topic_response = await client.post("/topics", json=topic_payload, headers=headers)
    assert topic_response.status_code == 201

    get_all_response = await client.get("/topics", headers=headers)
    assert get_all_response.status_code == 200
    topics = get_all_response.json()
    assert len(topics) > 0
    topic_id = next(
        (topic["id"] for topic in topics if topic["title"] == "FastAPI"), None
    )
    assert topic_id is not None

    return topic_id


@pytest.mark.asyncio
async def test_create_topic_ok(client, user_headers):
    topic_payload = {
        "title": "FastAPI",
        "skill": "Backend Development",
        "description": "Python async backend framework",
        "category": "Frameworks",
        "is_active": True,
    }

    topic_response = await client.post(
        "/topics", json=topic_payload, headers=user_headers
    )
    assert topic_response.status_code == 201


@pytest.mark.asyncio
async def test_get_topic(client, user_headers):
    topic_id = await create_topic_and_get_id(client, user_headers)

    get_id_response = await client.get(f"/topics/{topic_id}", headers=user_headers)
    assert get_id_response.status_code == 200
    topic = get_id_response.json()
    assert topic["title"] == "FastAPI"


@pytest.mark.asyncio
async def test_update_topic(client, user_headers):
    topic_id = await create_topic_and_get_id(client, user_headers)

    update_topic_payload = {
        "title": "PostgreSQL",
        "skill": "SQL Databases",
        "description": "The world's most advanced open-source, object-relational database",
        "category": "Databases",
        "is_active": True,
    }

    update_topic_response = await client.put(
        f"/topics/{topic_id}", json=update_topic_payload, headers=user_headers
    )
    assert update_topic_response.status_code == 200

    get_topic_response = await client.get(f"/topics/{topic_id}", headers=user_headers)
    assert get_topic_response.status_code == 200
    topic = get_topic_response.json()
    assert topic["title"] == "PostgreSQL"


@pytest.mark.asyncio
async def test_patch_topic(client, user_headers):
    topic_id = await create_topic_and_get_id(client, user_headers)

    patch_topic_response = await client.patch(
        f"/topics/{topic_id}", json={"is_active": False}, headers=user_headers
    )
    assert patch_topic_response.status_code == 200

    get_topic_response = await client.get(f"/topics/{topic_id}", headers=user_headers)
    assert get_topic_response.status_code == 200
    topic = get_topic_response.json()
    assert topic["is_active"] is False


@pytest.mark.asyncio
async def test_delete_topic(client, user_headers):
    topic_id = await create_topic_and_get_id(client, user_headers)

    delete_topic_response = await client.delete(
        f"/topics/{topic_id}", headers=user_headers
    )
    assert delete_topic_response.status_code == 200

    get_topic_response = await client.get(f"/topics/{topic_id}", headers=user_headers)
    assert get_topic_response.status_code == 404
