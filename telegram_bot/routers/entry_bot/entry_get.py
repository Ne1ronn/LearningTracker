from aiogram import Router, types, F
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, CallbackQuery, ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from .entry_router import router
import httpx

API_URL = "http://127.0.0.1:8000/entries/{entry_id}"
API_ALL_URL = "http://127.0.0.1:8000/entries"
API_GET_URL = "http://127.0.0.1:8000/token/{telegram_id}"
API_TOKEN_URL = "http://127.0.0.1:8000/auth/validate"
API_DATE_URL = "http://127.0.0.1:8000/entries/date/{target_date}"

class GetEntryState(StatesGroup):
    waiting_id = State()

class MyCallback(CallbackData, prefix="entries"):
    action: str
    fields: str | None = None

class EntriesState(StatesGroup):
    waiting_private = State()

def create_filter_buttons():
    builder = InlineKeyboardBuilder()
    builder.button(text="Private",
                   callback_data=MyCallback(action="ask_private", fields="private").pack())
    builder.button(text="Date",
                   callback_data=MyCallback(action="ask_date", fields="date").pack())
    builder.button(text="Mood",
                   callback_data=MyCallback(action="ask_mood", fields="mood").pack())
    builder.button(text="Progress",
                   callback_data=MyCallback(action="ask_progress", fields="progress_score").pack())
    builder.button(text="Hours",
                   callback_data=MyCallback(action="ask_hours", fields="mood_score").pack())

    return builder.as_markup()

def create_private_reply_buttons():
    builder = ReplyKeyboardBuilder()
    builder.button(text="Only private")
    builder.button(text="Only public")
    builder.button(text="All")

    return builder.as_markup()

@router.message(Command("get_all_entries"))
async def get_all_entries(message: types.Message, state: FSMContext):
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

    await state.update_data(
        filters={
            "private": None,
            "target_date": None,
            "min_mood_score": None,
            "max_mood_score": None,
            "min_progress_score": None,
            "max_progress_score": None,
            "min_learning_hours": None,
            "max_learning_hours": None,
        },
        sort=None,
        limit=20,
        offset=0,
    )

    await message.answer(f"Choose the filter method:", reply_markup=create_filter_buttons())
    # async with httpx.AsyncClient() as client:
    #     response = await client.get(API_ALL_URL, headers={"Authorization": f"Bearer {token}"})
    #
    # if response.status_code == 200:
    #     data = response.json()
    #
    #     for entry in data:
    #         await message.answer(
    #             f"Your entry data:\n"
    #             f"Entry id: {entry['id']}\n"
    #             f"Entry title: {entry['title']}\n"
    #             f"Entry description: {entry['description']}\n"
    #             f"Entry tags: {entry['tags']}\n"
    #             f"Entry mood_score: {entry['mood_score']}\n"
    #             f"Entry progress_score: {entry['progress_score']}\n"
    #             f"Entry learning_hours: {entry['learning_hours']}\n"
    #             f"Entry private: {entry['private']}"
    #         )
    # else:
    #     await message.answer(f"Error: {response.text}")
    #
    # await state.clear()

@router.callback_query(MyCallback.filter(F.action == "ask_private"))
async def ask_private(cb: CallbackQuery, state: FSMContext):
    await state.set_state(EntriesState.waiting_private)
    await cb.message.answer(
        "Choose the private:",
        reply_markup = create_private_reply_buttons()
    )
    await cb.answer()

@router.message(EntriesState.waiting_private)
async def set_private(message: types.Message, state: FSMContext):
    text = message.text

    if text == "All":
        value = None
    elif text == "Only private":
        value = True
    elif text == "Only public":
        value = False
    else:
        return

    data = await state.get_data()
    data["filters"]["private"] = value
    await state.update_data(data)

    await message.answer(
        "Private filter updated ✅",
        reply_markup = ReplyKeyboardRemove(),
    )

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