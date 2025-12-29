from aiogram import Router, types
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from .entry_router import router
import httpx

API_URL = "http://127.0.0.1:8000/entries/summary"
API_GET_URL = "http://127.0.0.1:8000/token/{telegram_id}"
API_TOKEN_URL = "http://127.0.0.1:8000/auth/validate"

@router.message(Command('summary'))
async def summary(message: types.Message, state: FSMContext):
    telegram_id = message.from_user.id
    async with httpx.AsyncClient() as client:
        response = await client.get(API_GET_URL.format(telegram_id=telegram_id))

    if response.status_code != 200:
        await message.answer(f"User with telegram id {telegram_id} unauthorized. Use command /login for authorize")
        await state.clear()
        return

    token = response.json().get("access_token")

    async with httpx.AsyncClient() as client:
        response = await client.get(API_TOKEN_URL, headers={"Authorization": f"Bearer {token}"})

    if response.status_code != 200:
        await message.answer(f"User didn't authorize. Use command /login for authorize")
        await state.clear()
        return

    await state.update_data(token=token)

    async with httpx.AsyncClient() as client:
        response = await client.get(API_URL, headers={"Authorization": f"Bearer {token}"})

    if response.status_code != 200:
        await message.answer("Received some error")
        await state.clear()

    data = response.json()
    lines = []
    for topics, hours in data.items():
        lines.append(f"{topics}: {hours} hours")

    text = f"Statistics by topics:\n\n" + "\n".join(lines)
    await message.answer(text)