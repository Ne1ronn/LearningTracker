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
        private_emoji = "🔒" if data['private'] else "🌐"
        mood_emoji = "😄" if data['mood_score'] >= 8 else "😐" if data['mood_score'] == 5 else "😔"

        text = (
            f"{private_emoji} <b>{data['title']}</b>\n"
            f"\n"
            f"📝 {data['description']}\n"
            f"\n"
            f"🏷 <i>{data['tags'] if data['tags'] else 'no tags'}</i>\n"
            f"\n"
            f"{mood_emoji} Mood: <b>{data['mood_score']}/10</b>  "
            f"⭐️ Progress: <b>{data['progress_score']}/10</b>  "
            f"⏱ <b>{data['learning_hours']}ч</b>\n"
            f"🆔 <code>{data['id']}</code>"
        )

        await message.answer(text, parse_mode="HTML")
    else:
        await message.answer(f"Error:{response.text}")
        await state.clear()
        return

    await state.clear()