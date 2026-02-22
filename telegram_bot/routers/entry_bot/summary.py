from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from .entry_router import router
import httpx

API_URL = "http://127.0.0.1:8000/entries/summary"

@router.callback_query(F.data == "summary")
async def summary(cb: CallbackQuery, state: FSMContext, token: str):
    await state.clear()
    await cb.answer()

    await state.update_data(token=token)

    async with httpx.AsyncClient() as client:
        response = await client.get(API_URL, headers={"Authorization": f"Bearer {token}"})

    if response.status_code != 200:
        await cb.message.answer("Received some error")
        await state.clear()

    data = response.json()
    lines = []
    for topics, hours in data.items():
        lines.append(f"{topics}: {hours} hours")

    text = f"Statistics by topics:\n\n" + "\n".join(lines)
    await cb.message.answer(text)