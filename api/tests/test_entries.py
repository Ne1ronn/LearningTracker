import pytest


async def create_entry_and_get_id(client, headers, entry_payload):
    response = await client.post("/entries", json=entry_payload, headers=headers)
    assert response.status_code == 201

    get_all_response = await client.get("/entries", headers=headers)
    assert get_all_response.status_code == 200
    entries = get_all_response.json()
    assert len(entries) > 0
    entry_id = next(
        (entry["id"] for entry in entries if entry["title"] == entry_payload["title"]),
        None,
    )
    assert entry_id is not None

    return entry_id


@pytest.mark.asyncio
async def test_create_entry_ok(client, user_headers, entry_payload):

    authorized_response = await client.post(
        "/entries", json=entry_payload, headers=user_headers
    )
    assert authorized_response.status_code == 201


@pytest.mark.asyncio
async def test_create_entry_401(client, entry_payload):
    unauthorized_response = await client.post("/entries", json=entry_payload)
    assert unauthorized_response.status_code == 401


@pytest.mark.asyncio
async def test_create_entry_422(client, user_headers):
    unauthorized_response = await client.post("/entries", headers=user_headers)
    assert unauthorized_response.status_code == 422


@pytest.mark.asyncio
async def test_get_entry_ok(client, user_headers, entry_payload):
    entry_id = await create_entry_and_get_id(client, user_headers, entry_payload)

    get_id_response = await client.get(f"/entries/{entry_id}", headers=user_headers)
    assert get_id_response.status_code == 200
    entry = get_id_response.json()
    assert entry["title"] == entry_payload["title"]


@pytest.mark.asyncio
async def test_get_entry_404(client, user_headers, entry_payload):
    get_all_response = await client.get("/entries", headers=user_headers)
    assert get_all_response.status_code == 200
    entries = get_all_response.json()
    if entries:
        max_id = max(entry["id"] for entry in entries)
    else:
        max_id = 0
    missed_id = max_id + 1000000

    get_id_response = await client.get(f"/entries/{missed_id}", headers=user_headers)
    assert get_id_response.status_code == 404


@pytest.mark.asyncio
async def test_update_entry(client, user_headers, entry_payload):
    entry_id = await create_entry_and_get_id(client, user_headers, entry_payload)

    entry_update_payload = dict(entry_payload)
    entry_update_payload["title"] = "Day 2"
    entry_update_payload["description"] = "Learned FastAPI"

    response = await client.put(
        f"/entries/{entry_id}", json=entry_update_payload, headers=user_headers
    )
    assert response.status_code == 200

    get_id_response = await client.get(f"/entries/{entry_id}", headers=user_headers)
    assert get_id_response.status_code == 200
    entry = get_id_response.json()
    assert entry["title"] == entry_update_payload["title"]


@pytest.mark.asyncio
async def test_patch_entry(client, user_headers, entry_payload):
    entry_id = await create_entry_and_get_id(client, user_headers, entry_payload)

    response = await client.patch(
        f"/entries/{entry_id}", json={"private": True}, headers=user_headers
    )
    assert response.status_code == 200

    get_id_response = await client.get(f"/entries/{entry_id}", headers=user_headers)
    assert get_id_response.status_code == 200
    entry = get_id_response.json()
    assert entry["private"] is True


@pytest.mark.asyncio
async def test_delete_entry(client, user_headers, entry_payload):
    entry_id = await create_entry_and_get_id(client, user_headers, entry_payload)

    response = await client.delete(f"/entries/{entry_id}", headers=user_headers)
    assert response.status_code == 200

    get_id_response = await client.get(f"/entries/{entry_id}", headers=user_headers)
    assert get_id_response.status_code == 404
