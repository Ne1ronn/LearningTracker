from aiogram import BaseMiddleware
import httpx
from aiogram.types import CallbackQuery
from .routers.topic_bot.topic_states import GetTopicState
from telegram_bot.keyboards import create_auth_buttons

API_GET_URL = "http://127.0.0.1:8000/token/{telegram_id}"
API_TOKEN_URL = "http://127.0.0.1:8000/auth/validate"
API_ADMIN_URL = "http://127.0.0.1:8000/auth/validate/admin"

class AuthMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        state = data.get("state")
        telegram_id = event.from_user.id
        async with httpx.AsyncClient() as client:
            response = await client.get(API_GET_URL.format(telegram_id=telegram_id))

        if response.status_code != 200:
            await event.answer(f"User with telegram id {telegram_id} unauthorized. Use this buttons to authorize", reply_markup=create_auth_buttons())
            await state.clear()
            return

        token = response.json().get("access_token")

        async with httpx.AsyncClient() as client:
            response = await client.get(API_TOKEN_URL, headers={"Authorization": f"Bearer {token}"})

        if response.status_code != 200:
            await event.answer(f"User didn't authorize. Use this buttons to authorize", reply_markup=create_auth_buttons())
            await state.clear()
            return

        data["token"] = token
        return await handler(event, data)

class RoleMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        state = data.get("state")
        token = data.get("token")

        if isinstance(event, CallbackQuery) and event.data == "get_topic":
            return await handler(event, data)

        if state:
            current_state = await state.get_state()
            if current_state == GetTopicState.waiting_id.state:
                return await handler(event, data)

        async with httpx.AsyncClient() as client:
            response = await client.get(API_ADMIN_URL, headers={"Authorization": f"Bearer {token}"})

        if response.status_code != 200:
            await event.answer("You don't have enough permissions")
            await state.clear()
            return

        return await handler(event, data)