from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from ...middleware import AuthMiddleware
import httpx

API_URL = "http://127.0.0.1:8000/logout"

logout_router = Router()
logout_router.callback_query.middleware(AuthMiddleware())

@logout_router.callback_query(F.data == "logout")
async def logout(cb: CallbackQuery, state: FSMContext, refresh_token: str):
    await state.clear()
    await cb.answer()

    async with httpx.AsyncClient() as client:
        response = await client.post(API_URL, json={"token": refresh_token})

    if response.status_code != 200:
        await cb.message.answer(f"Error:{response.text}")
        await state.clear()
        return

    await cb.message.answer("Successfully logged out")