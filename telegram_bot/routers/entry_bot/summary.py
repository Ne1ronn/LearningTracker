from aiogram import Router, types
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from .entry_router import router
import httpx

API_URL = "http://127.0.0.1:8000/entries/summary"

@router.message(Command('summary'))
async def summary(message: types.Message, state: FSMContext):
    async with httpx.AsyncClient() as client:
        response = await client.get(API_URL)

    if response.status_code != 200:
        await message.answer("Received some error")

    data = response.json()
    lines = []
    for topics, hours in data.items():
        lines.append(f"{topics}: {hours} hours")

    text = f"Statistics by topics:\n\n" + "\n".join(lines)
    await message.answer(text)