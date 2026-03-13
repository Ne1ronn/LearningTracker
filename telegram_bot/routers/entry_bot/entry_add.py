import os

from aiogram import types, F
from .entry_states import EntryForm
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from .entry_router import router
from ...keyboards import (
    create_yes_no_buttons,
    create_cancel_button,
    create_topics_buttons,
)
import httpx

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
API_URL = f"{API_BASE_URL}/entries"
API_TOPICS_URL = f"{API_BASE_URL}/topics"


@router.callback_query(F.data == "add_entry")
async def start_entry(cb: CallbackQuery, state: FSMContext, token: str):
    await state.clear()
    await cb.answer()

    await state.update_data(token=token)
    await cb.message.answer(
        "Enter the title of entry:", reply_markup=create_cancel_button()
    )
    await state.set_state(EntryForm.title)


@router.message(EntryForm.title)
async def get_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Now the description:", reply_markup=create_cancel_button())
    await state.set_state(EntryForm.description)


@router.message(EntryForm.description)
async def get_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer(
        "Now the tags(separated by commas):", reply_markup=create_cancel_button()
    )
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
        await message.answer(
            "Enter number between 0 and 10", reply_markup=create_cancel_button()
        )
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
        await message.answer(
            "Enter number between 0 and 10", reply_markup=create_cancel_button()
        )
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
        await message.answer(
            "Enter number more than 0 and less than 24",
            reply_markup=create_cancel_button(),
        )
        return

    await state.update_data(learning_hours=hours)
    await message.answer(
        "Your entry will be private or not?",
        reply_markup=create_yes_no_buttons("private"),
    )
    await state.set_state(EntryForm.private)


@router.callback_query(EntryForm.private)
async def add_private(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    if cb.data == "yes_private":
        await state.update_data(private=True)
    elif cb.data == "no_private":
        await state.update_data(private=False)
    await cb.message.answer(
        "Do you want add id of related topics?",
        reply_markup=create_yes_no_buttons("topics"),
    )
    await state.set_state(EntryForm.waiting_ids)


@router.callback_query(EntryForm.waiting_ids)
async def wait_topics(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    if cb.data == "yes_topics":
        async with httpx.AsyncClient() as client:
            response = await client.get(API_TOPICS_URL)

        if response.status_code == 200:
            topics = response.json()
        else:
            await cb.message.answer(f"Received error: {response.text}")
            await add_entry(cb.message, state)
            return

        await cb.message.answer(
            "Add or clear topics:", reply_markup=create_topics_buttons(topics)
        )
        await state.update_data(
            topics=topics,
            topic_ids=[],
            topic_map={int(t["id"]): t["title"] for t in topics},
        )
        await state.set_state(EntryForm.topic_ids)
    elif cb.data == "no_topics":
        await add_entry(cb.message, state)
        return


@router.callback_query(EntryForm.topic_ids)
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
        await cb.message.answer(
            "Topics cleared", reply_markup=create_topics_buttons(topics)
        )
        return

    elif cb.data == "ready":
        await add_entry(cb.message, state)
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


async def add_entry(message: types.Message, state: FSMContext):
    data = await state.get_data()
    token = data.pop("token")
    data.pop("topic_map", None)
    data.pop("topics", None)

    async with httpx.AsyncClient() as client:
        response = await client.post(
            API_URL, json=data, headers={"Authorization": f"Bearer {token}"}
        )

    if response.status_code == 201:
        await message.answer(response.text + "✅")
    else:
        await message.answer(f"Error:{response.text}")
        await state.clear()
        return

    await state.clear()
