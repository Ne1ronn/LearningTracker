from aiogram import BaseMiddleware
import httpx

API_GET_URL = "http://127.0.0.1:8000/token/{telegram_id}"
API_TOKEN_URL = "http://127.0.0.1:8000/auth/validate"

class AuthMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        state = data.get("state")
        telegram_id = event.from_user.id
        async with httpx.AsyncClient() as client:
            response = await client.get(API_GET_URL.format(telegram_id=telegram_id))

        if response.status_code != 200:
            await event.answer(f"User with telegram id {telegram_id} unauthorized. Use command /login for authorize")
            await state.clear()
            return

        token = response.json().get("access_token")

        async with httpx.AsyncClient() as client:
            response = await client.get(API_TOKEN_URL, headers={"Authorization": f"Bearer {token}"})

        if response.status_code != 200:
            await event.answer(f"User didn't authorize. Use command /login for authorize")
            await state.clear()
            return

        data["token"] = token
        return await handler(event, data)