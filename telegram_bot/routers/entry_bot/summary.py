import os

from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from .entry_router import router
import httpx

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
API_URL = f"{API_BASE_URL}/entries/summary"


@router.callback_query(F.data == "summary")
async def summary(cb: CallbackQuery, state: FSMContext, token: str):
    await state.clear()
    await cb.answer()

    await state.update_data(token=token)

    async with httpx.AsyncClient() as client:
        response = await client.get(
            API_URL, headers={"Authorization": f"Bearer {token}"}
        )

    if response.status_code != 200:
        await cb.message.answer("Received some error")
        await state.clear()
        return

    data = response.json()
    lines = []
    for topic, hours in data.items():
        lines.append(f"  📌 {topic}: <b>{hours}h</b>")

    text = "📚 <b>Statistics by topics</b>\n\n" + "\n".join(lines)
    await cb.message.answer(text, parse_mode="HTML")

    await state.clear()
