import os

from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from .entry_router import router
import httpx

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
API_URL = f"{API_BASE_URL}/entries/streak"


@router.callback_query(F.data == "streak")
async def streak_handler(cb: CallbackQuery, state: FSMContext, token: str):
    await state.clear()
    await cb.answer()

    async with httpx.AsyncClient() as client:
        response = await client.get(
            API_URL, headers={"Authorization": f"Bearer {token}"}
        )

    if response.status_code != 200:
        await cb.message.answer(f"Error: {response.text}")
        await state.clear()
        return

    streak = response.json()
    streak_emoji = "🔥" if streak > 2 else "✨"

    await cb.message.answer(
        f"{streak_emoji} Streak: <b>{streak} days</b>", parse_mode="HTML"
    )
    await state.clear()
