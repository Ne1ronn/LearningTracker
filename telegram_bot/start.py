from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
import httpx

API_GET_URL = "http://127.0.0.1:8000/token/{telegram_id}"
API_TOKEN_URL = "http://127.0.0.1:8000/auth/validate"

router = Router()

def create_crud_reply_buttons():
    builder = InlineKeyboardBuilder()

    builder.button(text="➕Add new entry", callback_data="add_entry")
    builder.button(text="🔍Get entry", callback_data="get_entry")
    builder.button(text="📋Get all entries", callback_data="get_all_entries")
    builder.button(text="✏️Edit entry", callback_data="patch_entry")
    builder.button(text="🔁Completely update entry", callback_data="update_entry")
    builder.button(text="🗑Delete entry", callback_data="delete_entry")
    builder.button(text="📊Summary", callback_data="summary")

    builder.adjust(2)
    return builder.as_markup()

@router.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    await state.clear()
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

    await message.answer("Choose what you want to do:",
                         reply_markup=create_crud_reply_buttons())