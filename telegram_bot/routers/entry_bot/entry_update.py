from aiogram import types, F
from .entry_states import UpdateEntryForm
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from .entry_router import router
import httpx

API_URL = "http://127.0.0.1:8000/entries/{entry_id}"
API_PERMISSION_URL = "http://127.0.0.1:8000/entries/{entry_id}/edit"
API_GET_URL = "http://127.0.0.1:8000/token/{telegram_id}"
API_TOKEN_URL = "http://127.0.0.1:8000/auth/validate"

@router.callback_query(F.data == "update_entry")
async def start_update(cb: CallbackQuery, state: FSMContext, token: str):
    await state.clear()
    await cb.answer()

    await state.update_data(token=token)
    await cb.message.answer("Enter the id of entry:")
    await state.set_state(UpdateEntryForm.waiting_id)

@router.message(UpdateEntryForm.waiting_id)
async def get_entry(message: types.Message, state: FSMContext):
    try:
        entry_id = int(message.text)
    except ValueError:
        await message.answer("Enter a integer number")
        return

    data = await state.get_data()
    token = data["token"]

    async with httpx.AsyncClient() as client:
        response = await client.get(API_PERMISSION_URL.format(entry_id=entry_id), headers={"Authorization": f"Bearer {token}"})

    if response.status_code in (403, 404):
        await message.answer(response.text)
        return

    await state.update_data(entry_id=entry_id)
    await message.answer("Enter the updated title of entry:")
    await state.set_state(UpdateEntryForm.title)

@router.message(UpdateEntryForm.title)
async def get_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Now the updated description:")
    await state.set_state(UpdateEntryForm.description)

@router.message(UpdateEntryForm.description)
async def get_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Now the updated tags(separated by commas):")
    await state.set_state(UpdateEntryForm.tags)

@router.message(UpdateEntryForm.tags)
async def get_tags(message: types.Message, state: FSMContext):
    await state.update_data(tags=message.text)
    await message.answer("Now the updated mood score:")
    await state.set_state(UpdateEntryForm.mood_score)

@router.message(UpdateEntryForm.mood_score)
async def get_mood(message: types.Message, state: FSMContext):
    try:
        score = int(message.text)
        if not (0 <= score <= 10):
            raise ValueError
    except ValueError:
        await message.answer("Enter number between 0 and 10")
        return
    await state.update_data(mood_score=score)
    await message.answer("Now the updated progress score:")
    await state.set_state(UpdateEntryForm.progress_score)

@router.message(UpdateEntryForm.progress_score)
async def get_progress(message: types.Message, state: FSMContext):
    try:
        score = int(message.text)
        if not (0 <= score <= 10):
            raise ValueError
    except ValueError:
        await message.answer("Enter number between 0 and 10")
        return

    await state.update_data(progress_score=score)
    await message.answer("Now the updated learning hours:")
    await state.set_state(UpdateEntryForm.learning_hours)

@router.message(UpdateEntryForm.learning_hours)
async def get_hours(message: types.Message, state: FSMContext):
    try:
        hours = float(message.text)
        if hours < 0 or hours > 24:
            raise ValueError
    except ValueError:
        await message.answer("Enter number more than 0 and less than 24")
        return

    await state.update_data(learning_hours=hours)
    await message.answer("Your entry will be private or not?")
    await state.set_state(UpdateEntryForm.private)

@router.message(UpdateEntryForm.private)
async def get_private(message: types.Message, state: FSMContext):
    if message.text.lower() == "private" or message.text.lower() == "yes":
        await state.update_data(private=True)
    else:
        await state.update_data(private=False)
    await message.answer("Do you want add id of related topics?")
    await state.set_state(UpdateEntryForm.waiting_ids)

@router.message(UpdateEntryForm.waiting_ids)
async def waiting_ids(message: types.Message, state: FSMContext):
    if message.text.lower() == "yes":
        await message.answer("Enter the id's by square brackets: [1, 2]")
        await state.set_state(UpdateEntryForm.topic_ids)
    else:
        await update_entry(message, state)

@router.message(UpdateEntryForm.topic_ids)
async def add_topics(message: types.Message, state: FSMContext):
    text = message.text.strip()

    if not (text.startswith("[") and text.endswith("]")):
        await message.answer("Enter in this format: [1, 2, 3]")
        return

    items = text[1:-1].replace(" ", "").split(",")

    if not all(item.isdigit() for item in items):
        await message.answer("Enter only integers by comma: [1, 2, 3]")
        return

    topic_ids = list(map(int, items))
    await state.update_data(topic_ids=topic_ids)
    await update_entry(message, state)

async def update_entry(message: types.Message, state: FSMContext):
    data = await state.get_data()
    token = data.pop("token")
    entry_id = data.pop('entry_id')
    async with httpx.AsyncClient() as client:
        response = await client.put(API_URL.format(entry_id=entry_id), json=data, headers={"Authorization": f"Bearer {token}"})

    if response.status_code == 200:
        await message.answer("Entry successfully updated ✅")
    else:
        await message.answer(f"Error:{response.text}")

    await state.clear()