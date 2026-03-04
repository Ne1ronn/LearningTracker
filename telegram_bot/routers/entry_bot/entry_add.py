from aiogram import types, F
from .entry_states import EntryForm
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from .entry_router import router
from ...keyboards import create_yes_no_buttons, create_cancel_button
import httpx

API_URL = "http://127.0.0.1:8000/entries"

@router.callback_query(F.data == "add_entry")
async def start_entry(cb: CallbackQuery, state: FSMContext, token: str):
    await state.clear()
    await cb.answer()

    await state.update_data(token=token)
    await cb.message.answer("Enter the title of entry:", reply_markup=create_cancel_button())
    await state.set_state(EntryForm.title)

@router.message(EntryForm.title)
async def get_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Now the description:", reply_markup=create_cancel_button())
    await state.set_state(EntryForm.description)

@router.message(EntryForm.description)
async def get_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Now the tags(separated by commas):", reply_markup=create_cancel_button())
    await state.set_state(EntryForm.tags)

@router.message(EntryForm.tags)
async def get_tags(message: types.Message, state: FSMContext):
    await state.update_data(tags=message.text)
    await message.answer("Now the mood score:", reply_markup=create_cancel_button())
    await state.set_state(EntryForm.mood_score)

@router.message(EntryForm.mood_score)
async def get_mood(message: types.Message, state: FSMContext):
    try:
        score = int(message.text)
        if not (0 <= score <= 10):
            raise ValueError
    except ValueError:
        await message.answer("Enter number between 0 and 10", reply_markup=create_cancel_button())
        return
    await state.update_data(mood_score=score)
    await message.answer("Now the progress score:", reply_markup=create_cancel_button())
    await state.set_state(EntryForm.progress_score)

@router.message(EntryForm.progress_score)
async def get_progress(message: types.Message, state: FSMContext):
    try:
        score = int(message.text)
        if not (0 <= score <= 10):
            raise ValueError
    except ValueError:
        await message.answer("Enter number between 0 and 10", reply_markup=create_cancel_button())
        return

    await state.update_data(progress_score=score)
    await message.answer("Now the learning hours:", reply_markup=create_cancel_button())
    await state.set_state(EntryForm.learning_hours)

@router.message(EntryForm.learning_hours)
async def get_hours(message: types.Message, state: FSMContext):
    try:
        hours = float(message.text)
        if hours < 0 or hours > 24:
            raise ValueError
    except ValueError:
        await message.answer("Enter number more than 0 and less than 24", reply_markup=create_cancel_button())
        return

    await state.update_data(learning_hours=hours)
    await message.answer("Your entry will be private or not?", reply_markup=create_yes_no_buttons("private"))
    await state.set_state(EntryForm.private)

@router.callback_query(EntryForm.private)
async def add_private(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    if cb.data == "yes_private":
        await state.update_data(private=True)
    elif cb.data == "no_private":
        await state.update_data(private=False)
    await cb.message.answer("Do you want add id of related topics?", reply_markup=create_yes_no_buttons("topics"))
    await state.set_state(EntryForm.waiting_ids)

@router.callback_query(EntryForm.waiting_ids)
async def wait_topics(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    if cb.data == "yes_topics":
        await cb.message.answer("Enter the id's by square brackets: [1, 2]", reply_markup=create_cancel_button())
        await state.set_state(EntryForm.topic_ids)
    elif cb.data == "no_topics":
        await add_entry(cb.message, state)

@router.message(EntryForm.topic_ids)
async def add_topics(message: types.Message, state: FSMContext):
    text = message.text.strip()

    if not (text.startswith("[") and text.endswith("]")):
        await message.answer("Enter in this format: [1, 2, 3]", reply_markup=create_cancel_button())
        return

    items = text[1:-1].replace(" ", "").split(",")

    if not all(item.isdigit() for item in items):
        await message.answer("Enter only integers by comma: [1, 2, 3]", reply_markup=create_cancel_button())
        return

    topic_ids = list(map(int, items))
    await state.update_data(topic_ids=topic_ids)
    await add_entry(message, state)

async def add_entry(message: types.Message, state: FSMContext):
    data = await state.get_data()
    token = data.pop("token")
    async with httpx.AsyncClient() as client:
        response = await client.post(API_URL, json=data, headers={"Authorization": f"Bearer {token}"})

    if response.status_code == 201:
        await message.answer(response.text+"✅")
    else:
        await message.answer(f"Error:{response.text}")
        await state.clear()
        return

    await state.clear()