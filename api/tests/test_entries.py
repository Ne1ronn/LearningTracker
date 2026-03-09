import pytest

async def create_login_user(client, user_payload):
    await client.post("/register", json=user_payload)

    login = await client.post("/login", data={
        "username": user_payload["username"],
        "password": user_payload["password"],
    })
    assert login.status_code == 200
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    return headers

async def create_entry_and_get_id(client, headers):
    entry_payload = {
        "title": "Day 1",
        "description": "Learned SQLAlchemy",
        "tags": "python,sqlalchemy",
        "mood_score": 8,
        "progress_score": 7,
        "learning_hours": 2.5,
        "private": False,
        "topic_ids": []
    }

    response = await client.post("/entries", json=entry_payload, headers=headers)
    assert response.status_code == 201

    get_all_response = await client.get("/entries", headers=headers)
    assert get_all_response.status_code == 200
    entries = get_all_response.json()
    assert len(entries) > 0
    entry_id = next((entry["id"] for entry in entries if entry["title"] == "Day 1"), None)
    assert entry_id is not None

    return entry_id

@pytest.mark.asyncio
async def test_create_entry(client, user_payload):
    headers = await create_login_user(client, user_payload)

    entry_payload = {
        "title": "Day 1",
        "description": "Learned SQLAlchemy",
        "tags": "python,sqlalchemy",
        "mood_score": 8,
        "progress_score": 7,
        "learning_hours": 2.5,
        "private": False,
        "topic_ids": []
    }

    response = await client.post("/entries", json=entry_payload, headers=headers)
    assert response.status_code == 201

@pytest.mark.asyncio
async def test_get_entry(client, user_payload):
    headers = await create_login_user(client, user_payload)
    entry_id = await create_entry_and_get_id(client, headers)

    get_id_response = await client.get(f"/entries/{entry_id}", headers=headers)
    assert get_id_response.status_code == 200
    entry = get_id_response.json()
    assert entry["title"] == "Day 1"

@pytest.mark.asyncio
async def test_update_entry(client, user_payload):
    headers = await create_login_user(client, user_payload)
    entry_id = await create_entry_and_get_id(client, headers)

    entry_update_payload = {
        "title": "Day 2",
        "description": "Learned FastAPI",
        "tags": "python,fastapi",
        "mood_score": 9,
        "progress_score": 8,
        "learning_hours": 3,
        "private": False,
        "topic_ids": []
    }

    response = await client.put(f"/entries/{entry_id}", json=entry_update_payload, headers=headers)
    assert response.status_code == 200

    get_id_response = await client.get(f"/entries/{entry_id}", headers=headers)
    assert get_id_response.status_code == 200
    entry = get_id_response.json()
    assert entry["title"] == "Day 2"

@pytest.mark.asyncio
async def test_patch_entry(client, user_payload):
    headers = await create_login_user(client, user_payload)
    entry_id = await create_entry_and_get_id(client, headers)

    response = await client.patch(f"/entries/{entry_id}", json={"private": True}, headers=headers)
    assert response.status_code == 200

    get_id_response = await client.get(f"/entries/{entry_id}", headers=headers)
    assert get_id_response.status_code == 200
    entry = get_id_response.json()
    assert entry["private"] == True

@pytest.mark.asyncio
async def test_delete_entry(client, user_payload):
    headers = await create_login_user(client, user_payload)
    entry_id = await create_entry_and_get_id(client, headers)

    response = await client.delete(f"/entries/{entry_id}", headers=headers)
    assert response.status_code == 200

    get_id_response = await client.get(f"/entries/{entry_id}", headers=headers)
    assert get_id_response.status_code == 404