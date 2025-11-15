from aiogram import Router, types
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from .entry_router import router
import httpx

API_URL = "http://127.0.0.1:8000/entries/{entry_id}"

class DeleteEntryState(StatesGroup):
    waiting_id = State()

@router.message(Command("delete_entry"))
async def get_id(message: types.Message, state: FSMContext):
    await message.answer("Enter the id of entry:")
    await state.set_state(DeleteEntryState.waiting_id)

@router.message(DeleteEntryState.waiting_id)
async def delete_entry(message: types.Message, state: FSMContext):
    try:
        entry_id = int(message.text)
        if not entry_id.is_integer():
            raise ValueError
    except ValueError:
        await message.answer("Enter a integer number")
        return

    async with httpx.AsyncClient() as client:
        response = await client.delete(API_URL.format(entry_id=entry_id))

    if response.status_code == 200:
        await message.answer("Entry deleted successfully ✅")
    else:
        await message.answer("Entered a wrong id, try again ❌")
        return
    await state.clear()