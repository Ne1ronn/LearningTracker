import os

from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from .entry_router import router
import httpx

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
API_URL = f"{API_BASE_URL}/entries/stats/weekly"

@router.callback_query(F.data == "weekly_stats")
async def weekly_stats(cb: CallbackQuery, state: FSMContext, token: str):
    await state.clear()
    await cb.answer()

    async with httpx.AsyncClient() as client:
        response = await client.get(API_URL, headers={"Authorization": f"Bearer {token}"})

    if response.status_code != 200:
        await cb.message.answer(f"Error:{response.text}")
        await state.clear()
        return

    last_7_days_hours = response.json().get("last_7_days_hours")
    prev_7_days_hours = response.json().get("prev_7_days_hours")
    delta_percent = response.json().get("delta_percent")
    current_streak = response.json().get("current_streak")

    delta_emoji = "📈" if delta_percent > 0 else "📉" if delta_percent < 0 else "➡️"
    streak_emoji = "🔥" if current_streak > 2 else "✨"

    text = (
        "📊 <b>Your statistics:</b>\n\n"
        f"⏱ This week: <b>{last_7_days_hours}h</b>\n"
        f"⏱ Previous week: <b>{prev_7_days_hours}h</b>\n"
        f"{delta_emoji} Changes: <b>{delta_percent:+.1f}%</b>\n\n"
        f"{streak_emoji} Streak: <b>{current_streak} days</b>"
    )
    await cb.message.answer(text, parse_mode="HTML")

    await state.clear()