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


async def create_goal_payload(client, headers):
    topic_id = await create_topic_and_get_id(client, headers)

    goal_payload = {
        "topic_id": topic_id,
        "target_date": "2026-01-01",
        "target_hours": 10,
    }

    response = await client.post("/goals", json=goal_payload, headers=headers)
    assert response.status_code == 201
    get_all_response = await client.get("/goals", headers=headers)
    assert get_all_response.status_code == 200
    goals = get_all_response.json()
    assert len(goals) > 0
    goal_id = next(
        (goal["id"] for goal in goals if goal["topic_id"] == goal_payload["topic_id"]),
        None,
    )
    assert goal_id is not None

    return goal_id, topic_id


@pytest.mark.asyncio
async def test_create_goal(client, user_headers):
    topic_id = await create_topic_and_get_id(client, user_headers)

    goal_payload = {
        "topic_id": topic_id,
        "target_date": "2026-01-01",
        "target_hours": 10,
    }

    response = await client.post("/goals", json=goal_payload, headers=user_headers)
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_create_goal_401(client, user_headers):
    topic_id = await create_topic_and_get_id(client, user_headers)

    goal_payload = {
        "topic_id": topic_id,
        "target_date": "2026-01-01",
        "target_hours": 10,
    }

    unauthorized_response = await client.post("/goals", json=goal_payload)
    assert unauthorized_response.status_code == 401


@pytest.mark.asyncio
async def test_create_goal_422(client, user_headers):
    unauthorized_response = await client.post("/goals", headers=user_headers)
    assert unauthorized_response.status_code == 422


@pytest.mark.asyncio
async def test_get_goal_ok(client, user_headers):
    goal_id, topic_id = await create_goal_payload(client, user_headers)

    get_id_response = await client.get(f"/goals/{goal_id}", headers=user_headers)
    assert get_id_response.status_code == 200
    goal = get_id_response.json()
    assert goal["topic_id"] == topic_id


@pytest.mark.asyncio
async def test_patch_goal(client, user_headers):
    goal_id, topic_id = await create_goal_payload(client, user_headers)

    response = await client.patch(
        f"/goals/{goal_id}", json={"target_hours": 5}, headers=user_headers
    )
    assert response.status_code == 200

    get_id_response = await client.get(f"/goals/{goal_id}", headers=user_headers)
    assert get_id_response.status_code == 200
    goal = get_id_response.json()
    assert goal["target_hours"] == 5


@pytest.mark.asyncio
async def test_delete(client, user_headers):
    goal_id, topic_id = await create_goal_payload(client, user_headers)

    response = await client.delete(f"/goals/{goal_id}", headers=user_headers)
    assert response.status_code == 200

    get_id_response = await client.get(f"/goals/{goal_id}", headers=user_headers)
    assert get_id_response.status_code == 404
