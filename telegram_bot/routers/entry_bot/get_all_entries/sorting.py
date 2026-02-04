from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, ReplyKeyboardRemove
from ..entry_states import EntriesState
from telegram_bot.keyboards import create_choose_buttons, create_sort_buttons, create_choose_reply_buttons
from ..entry_router import router

@router.callback_query(F.data == "ask_sort")
async def ask_sort(cb: CallbackQuery):
    await cb.message.answer(
        "Choose the sorting method:",
        reply_markup=create_sort_buttons()
    )
    await cb.answer()

@router.callback_query(F.data == "sort_date")
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

    await message.answer(
        f"Choose the sorting or filtering of result, or show the result:",
        reply_markup=create_choose_buttons(),
    )

@router.callback_query(F.data == "sort_mood")
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

    await message.answer(
        f"Choose the sorting or filtering of result, or show the result:",
        reply_markup=create_choose_buttons(),
    )

@router.callback_query(F.data == "sort_progress")
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

    await message.answer(
        f"Choose the sorting or filtering of result, or show the result:",
        reply_markup=create_choose_buttons(),
    )

@router.callback_query(F.data == "sort_hours")
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

    await message.answer(
        f"Choose the sorting or filtering of result, or show the result:",
        reply_markup=create_choose_buttons(),
    )

def asc_or_desc(text, sort: str):
    if text == "Ascending":
        return sort
    elif text == "Descending":
        return f"-{sort}"
    else:
        return False