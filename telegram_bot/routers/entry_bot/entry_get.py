from datetime import date, timedelta, datetime
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
    waiting_date = State()
    waiting_mood = State()
    waiting_progress = State()
    waiting_hours = State()
    sort_date = State()
    sort_mood = State()
    sort_progress = State()
    sort_hours = State()

def is_valid_date(s: str) -> bool:
    try:
        datetime.strptime(s, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def create_choose_buttons():
    builder = InlineKeyboardBuilder()

    builder.button(text="Filtering",
                   callback_data=MyCallback(action="ask_filter", fields="filter").pack())
    builder.button(text="Sorting",
                   callback_data=MyCallback(action="ask_sort", fields="sort").pack())

    return builder.as_markup()

def create_sort_buttons():
    builder = InlineKeyboardBuilder()
    builder.button(text="Date",
                   callback_data=MyCallback(action="sort_date", fields="created_at").pack())
    builder.button(text="Mood",
                   callback_data=MyCallback(action="sort_mood", fields="mood").pack())
    builder.button(text="Progress",
                   callback_data=MyCallback(action="sort_progress", fields="progress").pack())
    builder.button(text="Hours",
                   callback_data=MyCallback(action="sort_hours", fields="learning").pack())

    return builder.as_markup()

def create_choose_reply_buttons():
    builder = ReplyKeyboardBuilder()

    builder.button(text="Ascending")
    builder.button(text="Descending")

    return builder.as_markup()

def create_filter_buttons():
    builder = InlineKeyboardBuilder()
    builder.button(text="Private",
                   callback_data=MyCallback(action="ask_private", fields="private").pack())
    builder.button(text="Date",
                   callback_data=MyCallback(action="ask_date", fields="date").pack())
    builder.button(text="Mood",
                   callback_data=MyCallback(action="ask_mood", fields="mood_score").pack())
    builder.button(text="Progress",
                   callback_data=MyCallback(action="ask_progress", fields="progress_score").pack())
    builder.button(text="Hours",
                   callback_data=MyCallback(action="ask_hours", fields="learning_hours").pack())

    return builder.as_markup()

def create_private_reply_buttons():
    builder = ReplyKeyboardBuilder()

    builder.button(text="Only private")
    builder.button(text="Only public")
    builder.button(text="All")

    return builder.as_markup()

def create_date_reply_buttons():
    builder = ReplyKeyboardBuilder()

    builder.button(text="Today")
    builder.button(text="Yesterday")

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

    await message.answer(
        f"Choose the sorting or filtering of result:",
        reply_markup=create_choose_buttons()
    )
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

@router.callback_query(MyCallback.filter(F.action == "ask_filter"))
async def ask_filter(cb: CallbackQuery):
    await cb.message.answer(
        "Choose the filter method:",
        reply_markup=create_filter_buttons()
    )

    await cb.answer()

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
        await message.answer("Choose from buttons, try again:")
        return

    await state.update_data(private=value)
    await message.answer(
        "Private filter updated ✅",
        reply_markup = ReplyKeyboardRemove(),
    )

    await message.answer(
        "Choose next filter method or show the result:",
        reply_markup = create_filter_buttons()
    )

@router.callback_query(MyCallback.filter(F.action == "ask_date"))
async def ask_date(cb: CallbackQuery, state: FSMContext):
    await state.set_state(EntriesState.waiting_date)
    await cb.message.answer(
        "Choice the day or enter your own in YYYY-MM-DD format:",
        reply_markup = create_date_reply_buttons()
    )
    await cb.answer()

@router.message(EntriesState.waiting_date)
async def set_date(message: types.Message, state: FSMContext):
    text = message.text

    if text == "Today":
        d = date.today()
    elif text == "Yesterday":
        d = date.today() - timedelta(days=1)
    elif is_valid_date(text):
        d = datetime.strptime(text, "%Y-%m-%d")
    else:
        await message.answer("Incorrect date format ❌, try again:")
        return

    await state.update_data(date=d)

    await message.answer(
        "Date filter updated ✅",
        reply_markup = ReplyKeyboardRemove(),
    )

    await message.answer(
        "Choose next filter method or show the result:",
        reply_markup = create_filter_buttons()
    )

@router.callback_query(MyCallback.filter(F.action == "ask_mood"))
async def ask_mood(cb: CallbackQuery, state: FSMContext):
    await state.set_state(EntriesState.waiting_mood)
    await cb.message.answer(
        "Enter a range of numbers from 1 to 10 with a space between them:"
    )
    await cb.answer()

@router.message(EntriesState.waiting_mood)
async def set_mood(message: types.Message, state: FSMContext):
    try:
        low, high = map(int, message.text.split())
        if not (1 <= low <= high <= 10):
            raise ValueError
    except ValueError:
        await message.answer("Wrong input, try again:")
        return

    await state.update_data(min_mood_score=low, max_mood_score=high)
    await message.answer("Mood filter updated ✅")

@router.callback_query(MyCallback.filter(F.action == "ask_progress"))
async def ask_progress(cb: CallbackQuery, state: FSMContext):
    await state.set_state(EntriesState.waiting_progress)
    await cb.message.answer(
        "Enter a range of numbers from 1 to 10 with a space between them:"
    )
    await cb.answer()

@router.message(EntriesState.waiting_progress)
async def set_progress(message: types.Message, state: FSMContext):
    try:
        low, high = map(int, message.text.split())
        if not (1 <= low <= high <= 10):
            raise ValueError
    except ValueError:
        await message.answer("Wrong input, try again:")
        return

    await state.update_data(min_progress_score=low, max_progress_score=high)
    await message.answer("Progress filter updated ✅")

    await message.answer(
        "Choose next filter method or show the result:",
        reply_markup = create_filter_buttons()
    )

@router.callback_query(MyCallback.filter(F.action == "ask_hours"))
async def ask_hours(cb: CallbackQuery, state: FSMContext):
    await state.set_state(EntriesState.waiting_hours)
    await cb.message.answer(
        "Enter a range of numbers with a space between them:"
    )
    await cb.answer()

@router.message(EntriesState.waiting_hours)
async def set_hours(message: types.Message, state: FSMContext):
    try:
        low, high = map(int, message.text.split())
        if not (1 <= low <= high):
            raise ValueError
    except ValueError:
        await message.answer("Wrong input, try again:")
        return

    await state.update_data(min_learning_hours=low, max_learning_hours=high)
    await message.answer("Hours filter updated ✅")

    await message.answer(
        "Choose next filter method or show the result:",
        reply_markup = create_filter_buttons()
    )

@router.callback_query(MyCallback.filter(F.action == "ask_sort"))
async def ask_sort(cb: CallbackQuery):
    await cb.message.answer(
        "Choose the sorting method:",
        reply_markup=create_sort_buttons()
    )
    await cb.answer()

@router.callback_query(MyCallback.filter(F.action == "sort_date"))
async def sort_date(cb: CallbackQuery, state: FSMContext):
    await state.set_state(EntriesState.sort_date)
    await cb.message.answer(
        "Choose the sorting method:",
        reply_markup=create_choose_reply_buttons()
    )
    await cb.answer()

@router.message(EntriesState.sort_date)
async def set_sort_date(message: types.Message, state: FSMContext):
    text = message.text
    field = asc_or_desc(text, sort="created_at")

    if not field:
        await message.answer("Wrong input, try again:")
        return

    await state.update_data(sort=field)
    await message.answer("Sorting by date is enabled ✅",
                         reply_markup = ReplyKeyboardRemove(),)

@router.callback_query(MyCallback.filter(F.action == "sort_mood"))
async def sort_mood(cb: CallbackQuery, state: FSMContext):
    await state.set_state(EntriesState.sort_mood)
    await cb.message.answer(
        "Choose the sorting method:",
        reply_markup=create_choose_reply_buttons()
    )
    await cb.answer()

@router.message(EntriesState.sort_mood)
async def set_sort_mood(message: types.Message, state: FSMContext):
    text = message.text
    field = asc_or_desc(text, sort="mood")

    if not field:
        await message.answer("Wrong input, try again:")
        return

    await state.update_data(sort=field)
    await message.answer("Sorting by mood is enabled ✅",
                         reply_markup = ReplyKeyboardRemove(),)

@router.callback_query(MyCallback.filter(F.action == "sort_progress"))
async def sort_progress(cb: CallbackQuery, state: FSMContext):
    await state.set_state(EntriesState.sort_progress)
    await cb.message.answer(
        "Choose the sorting method:",
        reply_markup=create_choose_reply_buttons()
    )
    await cb.answer()

@router.message(EntriesState.sort_progress)
async def set_sort_progress(message: types.Message, state: FSMContext):
    text = message.text
    field = asc_or_desc(text, sort="progress")

    if not field:
        await message.answer("Wrong input, try again:")
        return

    await state.update_data(sort=field)
    await message.answer("Sorting by progress is enabled ✅",
                         reply_markup = ReplyKeyboardRemove())

@router.callback_query(MyCallback.filter(F.action == "sort_hours"))
async def sort_hours(cb: CallbackQuery, state: FSMContext):
    await state.set_state(EntriesState.sort_hours)
    await cb.message.answer(
        "Choose the sorting method:",
        reply_markup=create_choose_reply_buttons()
    )
    await cb.answer()

@router.message(EntriesState.sort_hours)
async def set_sort_hours(message: types.Message, state: FSMContext):
    text = message.text
    field = asc_or_desc(text, sort="hours")

    if not field:
        await message.answer("Wrong input, try again:")
        return

    await state.update_data(sort=field)
    await message.answer("Sorting by hours is enabled ✅",
                         reply_markup = ReplyKeyboardRemove(),)

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

def asc_or_desc(text, sort: str):
    if text == "Ascending":
        return sort
    elif text == "Descending":
        return f"-{sort}"
    else:
        return False