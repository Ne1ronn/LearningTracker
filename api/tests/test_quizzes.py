import pytest


async def create_entry_and_get_id(client, headers, entry_payload):
    entry_response = await client.post("/entries", json=entry_payload, headers=headers)
    assert entry_response.status_code == 201

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


async def create_quiz_payload(client, headers, entry_payload):
    entry_id = await create_entry_and_get_id(client, headers, entry_payload)
    quiz_payload = {
        "entry_id": entry_id,
        "question": "random",
        "answer": "random",
    }

    response = await client.post("/quizzes", json=quiz_payload, headers=headers)
    assert response.status_code == 201
    get_all_response = await client.get("/quizzes", headers=headers)
    assert get_all_response.status_code == 200
    quizzes = get_all_response.json()
    assert len(quizzes) > 0
    quiz_id = next(
        (
            quiz["id"]
            for quiz in quizzes
            if quiz["entry_id"] == quiz_payload["entry_id"]
        ),
        None,
    )
    assert quiz_id is not None

    return quiz_id, entry_id


@pytest.mark.asyncio
async def test_create_quiz(client, user_headers, entry_payload):
    entry_id = await create_entry_and_get_id(client, user_headers, entry_payload)

    quiz_payload = {
        "entry_id": entry_id,
        "question": "random",
        "answer": "random",
    }

    response = await client.post("/quizzes", json=quiz_payload, headers=user_headers)
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_create_quiz_401(client, user_headers, entry_payload):
    entry_id = await create_entry_and_get_id(client, user_headers, entry_payload)

    quiz_payload = {
        "entry_id": entry_id,
        "question": "random",
        "answer": "random",
    }

    unauthorized_response = await client.post("/quizzes", json=quiz_payload)
    assert unauthorized_response.status_code == 401


@pytest.mark.asyncio
async def test_create_quiz_422(client, user_headers):
    unauthorized_response = await client.post("/quizzes", headers=user_headers)
    assert unauthorized_response.status_code == 422


@pytest.mark.asyncio
async def test_get_quiz_ok(client, user_headers, entry_payload):
    quiz_id, entry_id = await create_quiz_payload(client, user_headers, entry_payload)

    get_id_response = await client.get(f"/quizzes/{quiz_id}", headers=user_headers)
    assert get_id_response.status_code == 200
    quiz = get_id_response.json()
    assert quiz["entry_id"] == entry_id


@pytest.mark.asyncio
async def test_patch_quiz(client, user_headers, entry_payload):
    quiz_id, entry_id = await create_quiz_payload(client, user_headers, entry_payload)

    response = await client.patch(
        f"/quizzes/{quiz_id}", json={"answer": "test"}, headers=user_headers
    )
    assert response.status_code == 200

    get_id_response = await client.get(f"/quizzes/{quiz_id}", headers=user_headers)
    assert get_id_response.status_code == 200
    quiz = get_id_response.json()
    assert quiz["answer"] == "test"


@pytest.mark.asyncio
async def test_delete_quiz(client, user_headers, entry_payload):
    quiz_id, entry_id = await create_quiz_payload(client, user_headers, entry_payload)

    response = await client.delete(f"/quizzes/{quiz_id}", headers=user_headers)
    assert response.status_code == 200

    get_id_response = await client.get(f"/quizzes/{quiz_id}", headers=user_headers)
    assert get_id_response.status_code == 404
