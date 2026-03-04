from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from .entry_states import GetEntryState
from .entry_router import router
import httpx

from ...keyboards import create_cancel_button

API_URL = "http://127.0.0.1:8000/entries/{entry_id}"

@router.callback_query(F.data == "get_entry")
async def start_entry(cb: CallbackQuery, state: FSMContext, token: str):
    await state.clear()
    await cb.answer()

    await state.update_data(token=token)
    await cb.message.answer("Enter the id of entry:", reply_markup=create_cancel_button())
    await state.set_state(GetEntryState.waiting_id)

@router.message(GetEntryState.waiting_id)
async def get_entry(message: types.Message, state: FSMContext):
    try:
        entry_id = int(message.text)
    except ValueError:
        await message.answer("Enter a integer number", reply_markup=create_cancel_button())
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
        return

    await state.clear()