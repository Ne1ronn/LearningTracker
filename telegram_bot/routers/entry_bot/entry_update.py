from aiogram import types, F
from .entry_states import UpdateEntryForm
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from .entry_router import router
import httpx

from ...keyboards import create_yes_no_buttons, create_cancel_button, create_topics_buttons

API_URL = "http://127.0.0.1:8000/entries/{entry_id}"
API_PERMISSION_URL = "http://127.0.0.1:8000/entries/{entry_id}/edit"
API_TOPICS_URL = "http://127.0.0.1:8000/topics"

@router.callback_query(F.data == "update_entry")
async def start_update(cb: CallbackQuery, state: FSMContext, token: str):
    await state.clear()
    await cb.answer()

    await state.update_data(token=token)
    await cb.message.answer("Enter the id of entry:", reply_markup=create_cancel_button())
    await state.set_state(UpdateEntryForm.waiting_id)

@router.message(UpdateEntryForm.waiting_id)
async def get_entry(message: types.Message, state: FSMContext):
    try:
        entry_id = int(message.text)
    except ValueError:
        await message.answer("Enter a integer number", reply_markup=create_cancel_button())
        return

    data = await state.get_data()
    token = data["token"]

    async with httpx.AsyncClient() as client:
        response = await client.get(API_PERMISSION_URL.format(entry_id=entry_id), headers={"Authorization": f"Bearer {token}"})

    if response.status_code in (403, 404):
        await message.answer(response.text)
        await state.clear()
        return

    await state.update_data(entry_id=entry_id)
    await message.answer("Enter the updated title of entry:", reply_markup=create_cancel_button())
    await state.set_state(UpdateEntryForm.title)

@router.message(UpdateEntryForm.title)
async def get_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Now the updated description:", reply_markup=create_cancel_button())
    await state.set_state(UpdateEntryForm.description)

@router.message(UpdateEntryForm.description)
async def get_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Now the updated tags(separated by commas):", reply_markup=create_cancel_button())
    await state.set_state(UpdateEntryForm.tags)

@router.message(UpdateEntryForm.tags)
async def get_tags(message: types.Message, state: FSMContext):
    await state.update_data(tags=message.text)
    await message.answer("Now the updated mood score:", reply_markup=create_cancel_button())
    await state.set_state(UpdateEntryForm.mood_score)

@router.message(UpdateEntryForm.mood_score)
async def get_mood(message: types.Message, state: FSMContext):
    try:
        score = int(message.text)
        if not (0 <= score <= 10):
            raise ValueError
    except ValueError:
        await message.answer("Enter number between 0 and 10", reply_markup=create_cancel_button())
        return
    await state.update_data(mood_score=score)
    await message.answer("Now the updated progress score:", reply_markup=create_cancel_button())
    await state.set_state(UpdateEntryForm.progress_score)

@router.message(UpdateEntryForm.progress_score)
async def get_progress(message: types.Message, state: FSMContext):
    try:
        score = int(message.text)
        if not (0 <= score <= 10):
            raise ValueError
    except ValueError:
        await message.answer("Enter number between 0 and 10", reply_markup=create_cancel_button())
        return

    await state.update_data(progress_score=score)
    await message.answer("Now the updated learning hours:", reply_markup=create_cancel_button())
    await state.set_state(UpdateEntryForm.learning_hours)

@router.message(UpdateEntryForm.learning_hours)
async def get_hours(message: types.Message, state: FSMContext):
    try:
        hours = float(message.text)
        if hours < 0 or hours > 24:
            raise ValueError
    except ValueError:
        await message.answer("Enter number more than 0 and less than 24", reply_markup=create_cancel_button())
        return

    await state.update_data(learning_hours=hours)
    await message.answer("Your entry will be private or not?", reply_markup=create_yes_no_buttons("private_update"))
    await state.set_state(UpdateEntryForm.private)

@router.callback_query(UpdateEntryForm.private)
async def add_private(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    if cb.data == "yes_private_update":
        await state.update_data(private=True)
    elif cb.data == "no_private_update":
        await state.update_data(private=False)
    await cb.message.answer("Do you want add id of related topics?", reply_markup=create_yes_no_buttons("topics_update"))
    await state.set_state(UpdateEntryForm.waiting_ids)

@router.callback_query(UpdateEntryForm.waiting_ids)
async def wait_topics(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    if cb.data == "yes_topics_update":
        async with httpx.AsyncClient() as client:
            response = await client.get(API_TOPICS_URL)

        if response.status_code == 200:
            topics = response.json()
        else:
            await cb.message.answer(f"Received error: {response.text}")
            await update_entry(cb.message, state)
            return

        await cb.message.answer("Choose the topics:", reply_markup=create_topics_buttons(topics))
        await state.update_data(topics=topics, topic_ids=[], topic_map={int(t["id"]): t["title"] for t in topics})
        await state.set_state(UpdateEntryForm.topic_ids)
    elif cb.data == "no_topics_update":
        await update_entry(cb.message, state)
        return

@router.callback_query(UpdateEntryForm.topic_ids)
async def add_topics(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    data = await state.get_data()
    topics = data["topics"]
    if cb.data == "cancel":
        await state.clear()
        await cb.message.answer("Operation cancelled")
        return

    elif cb.data == "clear":
        await state.update_data(topic_ids=[])
        await cb.message.answer("Topics cleared", reply_markup=create_topics_buttons(topics))
        return

    elif cb.data == "ready":
        await update_entry(cb.message, state)
        return

    elif cb.data.startswith("topic_"):
        topic_id = int(cb.data.split("_")[1])
        topics_ids = data["topic_ids"]

        if topic_id in topics_ids:
            await cb.message.answer(f"Topic {topic_id} already in list")
            return

        topics_ids.append(topic_id)

        topic_map = data["topic_map"]
        titles = [topic_map.get(i, str(i)) for i in topics_ids]
        text = "Selected topics:\n" + "\n".join(f"• {t}" for t in titles)

        await state.update_data(topic_ids=topics_ids)
        await cb.message.answer(text, reply_markup=create_topics_buttons(topics))
        return
    else:
        await cb.message.answer("Wrong button. Please choose right one")
        return

async def update_entry(message: types.Message, state: FSMContext):
    data = await state.get_data()
    token = data.pop("token")
    entry_id = data.pop('entry_id')
    data.pop("topic_map", None)
    async with httpx.AsyncClient() as client:
        response = await client.put(API_URL.format(entry_id=entry_id), json=data, headers={"Authorization": f"Bearer {token}"})

    if response.status_code == 200:
        await message.answer("Entry successfully updated ✅")
    else:
        await message.answer(f"Error:{response.text}")
        await state.clear()
        return

    await state.clear()