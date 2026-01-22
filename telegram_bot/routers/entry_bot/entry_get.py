from aiogram import Router, types
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from .entry_router import router
import httpx

API_URL = "http://127.0.0.1:8000/entries/{entry_id}"
API_GET_URL = "http://127.0.0.1:8000/token/{telegram_id}"
API_TOKEN_URL = "http://127.0.0.1:8000/auth/validate"
API_DATE_URL = "http://127.0.0.1:8000/entries/date/{target_date}"

class GetEntryState(StatesGroup):
    waiting_id = State()

class GetEntriesState(StatesGroup):
    waiting_date = State()

@router.message(Command("get_entry"))
async def start_entry(message: types.Message, state: FSMContext):
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
    await message.answer("Enter the id of entry:")
    await state.set_state(GetEntryState.waiting_id)

@router.message(GetEntryState.waiting_id)
async def get_entry(message: types.Message, state: FSMContext):
    try:
        entry_id = int(message.text)
        if not entry_id.is_integer():
            raise ValueError
    except ValueError:
        await message.answer("Enter a integer number")
        return

    data = await state.get_data()
    token = data.pop("token")

    async with httpx.AsyncClient() as client:
        response = await client.get(API_URL.format(entry_id=entry_id), headers={"Authorization": f"Bearer {token}"})

    if response.status_code == 200:
        data = response.json()
        await message.answer(
            f"Your entry data: \n"
            f"Entry id: {data['id']}\n"
            f"Entry title: {data['title']}\n"
            f"Entry description: {data['description']}\n"
            f"Entry tags: {data['tags']}\n"
            f"Entry mood_score: {data['mood_score']}\n"
            f"Entry progress_score: {data['progress_score']}\n"
            f"Entry learning_hours: {data['learning_hours']}\n"
            f"Entry private: {data['private']}")
    else:
        await message.answer(f"Error:{response.text}")

    await state.clear()

@router.message(Command("get_entries_by_date"))
async def start_get(message: types.Message, state: FSMContext):
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
    await message.answer("Enter the date:")
    await state.set_state(GetEntriesState.waiting_date)

@router.message(GetEntriesState.waiting_date)
async def get_entries(message: types.Message, state: FSMContext):
    data = await state.get_data()
    token = data.pop("token")

    async with httpx.AsyncClient() as client:
        response = await client.get(API_DATE_URL.format(target_date=message.text), headers={"Authorization": f"Bearer {token}"})

    if response.status_code == 200:
        data = response.json()  # list[dict]

        for entry in data:
            await message.answer(
                f"Your entry data:\n"
                f"Entry id: {entry['id']}\n"
                f"Entry title: {entry['title']}\n"
                f"Entry description: {entry['description']}\n"
                f"Entry tags: {entry['tags']}\n"
                f"Entry mood_score: {entry['mood_score']}\n"
                f"Entry progress_score: {entry['progress_score']}\n"
                f"Entry learning_hours: {entry['learning_hours']}\n"
                f"Entry private: {entry['private']}"
            )
    else:
        await message.answer(f"Error: {response.text}")

    await state.clear()