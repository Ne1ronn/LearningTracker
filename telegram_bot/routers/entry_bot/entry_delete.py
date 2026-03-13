import os

from aiogram import types, F
from .entry_states import DeleteEntryState
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from .entry_router import router
import httpx

from ...keyboards import create_cancel_button

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
API_URL = f"{API_BASE_URL}/entries/{{entry_id}}"


@router.callback_query(F.data == "delete_entry")
async def get_id(cb: CallbackQuery, state: FSMContext, token: str):
    await state.clear()
    await cb.answer()

    await state.update_data(token=token)
    await cb.message.answer(
        "Enter the id of entry:", reply_markup=create_cancel_button()
    )
    await state.set_state(DeleteEntryState.waiting_id)


@router.message(DeleteEntryState.waiting_id)
async def delete_entry(message: types.Message, state: FSMContext):
    try:
        entry_id = int(message.text)
    except ValueError:
        await message.answer(
            "Enter a integer number", reply_markup=create_cancel_button()
        )
        return

    data = await state.get_data()
    token = data.pop("token")
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            API_URL.format(entry_id=entry_id),
            headers={"Authorization": f"Bearer {token}"},
        )

    if response.status_code == 200:
        await message.answer("Entry deleted successfully ✅")
    else:
        await message.answer(response.text)
        await state.clear()
        return

    await state.clear()
