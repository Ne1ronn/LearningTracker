import pytest


@pytest.mark.asyncio
async def test_register(client, user_payload):
    response = await client.post("/register", json=user_payload)
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_register_conflict(client, user_payload):
    await client.post("/register", json=user_payload)
    response = await client.post("/register", json=user_payload)
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_login(client, user_payload):
    await client.post("/register", json=user_payload)

    form = {
        "username": user_payload["username"],
        "password": user_payload["password"],
    }
    response = await client.post("/login", data=form)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


@pytest.mark.asyncio
async def test_logout(client, user_payload):
    await client.post("/register", json=user_payload)

    response = await client.post(
        "/login",
        data={
            "username": user_payload["username"],
            "password": user_payload["password"],
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "refresh_token" in data
    refresh_token = data["refresh_token"]
    logout_response = await client.post("/logout", json={"token": refresh_token})
    assert logout_response.status_code == 200

    refresh_response = await client.post("/refresh", json={"token": refresh_token})
    assert refresh_response.status_code == 401


@pytest.mark.asyncio
async def test_auth_validation(client, user_payload):
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

    response = await client.get(
        "/auth/validate", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
