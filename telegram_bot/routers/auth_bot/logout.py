import os
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from ...keyboards import create_auth_buttons
from ...middleware import AuthMiddleware
import httpx

API_URL = "http://127.0.0.1:8000/logout"
API_DELETE_URL = "http://127.0.0.1:8000/token/{telegram_id}"

BOT_SECRET = os.getenv("BOT_SECRET")
logout_router = Router()
logout_router.callback_query.middleware(AuthMiddleware())

@logout_router.callback_query(F.data == "logout")
async def logout(cb: CallbackQuery, state: FSMContext, refresh_token: str | None = None):
    await state.clear()
    await cb.answer()

    if not refresh_token:
        await cb.message.answer("No credentials provided, use this buttons to authorize",
                                reply_markup=create_auth_buttons())
        await state.clear()
        return

    async with httpx.AsyncClient() as client:
        logout_response = await client.post(API_URL, json={"token": refresh_token})

        if logout_response.status_code != 200:
            await cb.message.answer(f"Error:{logout_response.text}")
            await state.clear()
            return

        telegram_id = cb.message.from_user.id

        delete_response = await client.delete(API_DELETE_URL.format(telegram_id=telegram_id), headers={"X-Bot-Secret": BOT_SECRET})
        if delete_response.status_code != 200:
            await cb.message.answer(f"Error:{delete_response.text}")

    await cb.message.answer("Successfully logged out")