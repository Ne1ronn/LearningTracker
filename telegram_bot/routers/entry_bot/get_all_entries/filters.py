from datetime import date, timedelta, datetime
from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, ReplyKeyboardRemove
from ..entry_states import EntriesState
from ..keyboards import create_date_reply_buttons, create_filter_buttons, create_choose_buttons, \
    create_private_reply_buttons
from ..entry_router import router

@router.callback_query(F.data == "ask_filter")
async def ask_filter(cb: CallbackQuery):
    await cb.message.answer(
        "Choose the filter method:",
        reply_markup=create_filter_buttons()
    )

    await cb.answer()

@router.callback_query(F.data == "ask_private")
async def ask_private(cb: CallbackQuery, state: FSMContext):
    await state.set_state(EntriesState.waiting_private)
    await cb.message.answer(
        "Choose the private:",
        reply_markup=create_private_reply_buttons()
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
        reply_markup=ReplyKeyboardRemove(),
    )

    await message.answer(
        f"Choose the sorting or filtering of result, or show the result:",
        reply_markup=create_choose_buttons(),
    )

@router.callback_query(F.data == "ask_date")
async def ask_date(cb: CallbackQuery, state: FSMContext):
    await state.set_state(EntriesState.waiting_date)
    await cb.message.answer(
        "Choice the day or enter your own in YYYY-MM-DD format:",
        reply_markup=create_date_reply_buttons()
    )
    await cb.answer()

@router.message(EntriesState.waiting_date)
async def set_date(message: types.Message, state: FSMContext):
    text = message.text

    if text == "Today":
        d = date.today()
    elif text == "Yesterday":
        d = date.today() - timedelta(days=1)
    elif text == "Clear filter":
        d = None
    elif is_valid_date(text):
        d = datetime.strptime(text, "%Y-%m-%d")
    else:
        await message.answer("Incorrect date format ❌, try again:")
        return

    await state.update_data(target_date=d)

    await message.answer(
        "Date filter updated ✅",
        reply_markup=ReplyKeyboardRemove(),
    )

    await message.answer(
        f"Choose the sorting or filtering of result, or show the result:",
        reply_markup=create_choose_buttons(),
    )

@router.callback_query(F.data == "ask_mood")
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

    await message.answer(
        f"Choose the sorting or filtering of result, or show the result:",
        reply_markup=create_choose_buttons(),
    )

@router.callback_query(F.data == "ask_progress")
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
        f"Choose the sorting or filtering of result, or show the result:",
        reply_markup=create_choose_buttons(),
    )

@router.callback_query(F.data == "ask_hours")
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
        f"Choose the sorting or filtering of result, or show the result:",
        reply_markup=create_choose_buttons(),
    )

def is_valid_date(s: str) -> bool:
    try:
        datetime.strptime(s, "%Y-%m-%d")
        return True
    except ValueError:
        return False