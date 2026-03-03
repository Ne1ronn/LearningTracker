from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from .entry_router import router
import httpx

API_URL = "http://127.0.0.1:8000/entries/stats/weekly"

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

    await cb.message.answer(
        f"Your hour stats for last 7 days: {last_7_days_hours}\n"
        f"Your hour stats for previous 7 days: {prev_7_days_hours}\n"
        f"Your delta percentage: {delta_percent}\n"
        f"Your current streak: {current_streak}"
    )

    await state.clear()