import os

from aiogram import BaseMiddleware
import httpx
from aiogram.types import CallbackQuery
from .routers.topic_bot.topic_states import GetTopicState
from telegram_bot.keyboards import create_auth_buttons

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
API_GET_URL = f"{API_BASE_URL}/token/{{telegram_id}}"
API_TOKEN_URL = f"{API_BASE_URL}/auth/validate"
API_ADMIN_URL = f"{API_BASE_URL}/auth/validate/admin"
API_REFRESH_URL = f"{API_BASE_URL}/refresh"
API_POST_URL = f"{API_BASE_URL}/token"
BOT_SECRET = os.getenv("BOT_SECRET")


class AuthMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        state = data.get("state")
        telegram_id = event.from_user.id
        async with httpx.AsyncClient() as client:
            token_response = await client.get(
                API_GET_URL.format(telegram_id=telegram_id),
                headers={"X-Bot-Secret": BOT_SECRET},
            )

            if token_response.status_code != 200:
                await event.answer(
                    f"User with telegram id {telegram_id} unauthorized. Use this buttons to authorize",
                    reply_markup=create_auth_buttons(),
                )
                await state.clear()
                return

            access_token = token_response.json().get("access_token")
            refresh_token = token_response.json().get("refresh_token")

            if not access_token or not refresh_token:
                await event.answer(
                    "Auth data missing. Use this buttons to authorize",
                    reply_markup=create_auth_buttons(),
                )
                await state.clear()
                return

            auth_response = await client.get(
                API_TOKEN_URL, headers={"Authorization": f"Bearer {access_token}"}
            )

            if auth_response.status_code != 200:
                if auth_response.status_code == 401:
                    refresh_response = await client.post(
                        API_REFRESH_URL, json={"token": refresh_token}
                    )

                    if refresh_response.status_code != 201:
                        await event.answer(
                            "Logged session ended. Use this buttons to authorize",
                            reply_markup=create_auth_buttons(),
                        )
                        await state.clear()
                        return

                    access_token = refresh_response.json().get("access_token")
                    refresh_token = refresh_response.json().get("refresh_token")

                    if not access_token or not refresh_token:
                        await event.answer(
                            "Auth data missing. Use this buttons to authorize",
                            reply_markup=create_auth_buttons(),
                        )
                        await state.clear()
                        return

                    response = await client.post(
                        API_POST_URL,
                        params={"telegram_id": telegram_id},
                        json={"token": refresh_token},
                        headers={
                            "Authorization": f"Bearer {access_token}",
                            "X-Bot-Secret": BOT_SECRET,
                        },
                    )

                    if response.status_code != 201:
                        await event.answer(f"{response.text}")
                        await state.clear()
                        return
                else:
                    await event.answer(f"Error: {auth_response.text}")
                    await state.clear()
                    return

        if not access_token or not refresh_token:
            await event.answer(
                "Auth data missing. Use this buttons to authorize",
                reply_markup=create_auth_buttons(),
            )
            await state.clear()
            return

        data["token"] = access_token
        data["refresh_token"] = refresh_token
        return await handler(event, data)


class RoleMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        state = data.get("state")
        token = data.get("token")

        if isinstance(event, CallbackQuery) and event.data in [
            "get_topic",
            "entry_actions",
        ]:
            return await handler(event, data)

        if state:
            current_state = await state.get_state()
            if current_state == GetTopicState.waiting_id.state:
                return await handler(event, data)

        async with httpx.AsyncClient() as client:
            response = await client.get(
                API_ADMIN_URL, headers={"Authorization": f"Bearer {token}"}
            )

        if response.status_code != 200:
            await event.answer("You don't have enough permissions")
            await state.clear()
            return

        return await handler(event, data)
