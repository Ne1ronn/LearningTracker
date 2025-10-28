from aiogram import Router, types
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
import httpx


router = Router()
API_URL = "http://127.0.0.1:8000/entries/{entry_id}"

class GetEntryState(StatesGroup):
    waiting_id = State()

@router.message(Command("get_entry"))
async def start_entry(message: types.Message, state: FSMContext):
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

    async with httpx.AsyncClient() as client:
        response = await client.get(API_URL.format(entry_id=entry_id))

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
            f"Entry learning_hours: {data['learning_hours']}")
    else:
        await message.answer(f"Error:{response.text}")

    await state.clear()
