import os
from datetime import datetime
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from httpx import AsyncClient
from .goal_router import router
from .goal_states import GoalAddState
from ...keyboards import create_topics_buttons, create_cancel_button

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
API_URL = f"{API_BASE_URL}/goals"
API_TOPICS_URL = f"{API_BASE_URL}/topics"


@router.callback_query(F.data == "add_goal")
async def start_handler(cb: CallbackQuery, state: FSMContext, token: str):
    await cb.answer()
    await state.clear()

    async with AsyncClient() as client:
        response = await client.get(
            API_TOPICS_URL, headers={"Authorization": f"Bearer {token}"}
        )

    if response.status_code == 200:
        topics = response.json()
    else:
        await cb.message.answer(f"Received error: {response.text}")
        await state.clear()
        return

    await cb.message.answer(
        "Choose the topic:",
        reply_markup=create_topics_buttons(topics, many_topics=False),
    )
    await state.update_data(
        topics=topics,
        token=token,
        topic_map={int(t["id"]): t["title"] for t in topics},
    )
    await state.set_state(GoalAddState.waiting_topic_id)


@router.callback_query(GoalAddState.waiting_topic_id)
async def add_topic_id(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    data = await state.get_data()
    topics = data["topics"]
    if cb.data == "cancel":
        await state.clear()
        await cb.message.answer("Operation cancelled")
        return

    elif cb.data == "ready":
        topic_id = data.get("topic_id")

        if topic_id is None:
            await cb.message.answer(
                f"Topic not chosen, choose the topic:",
                reply_markup=create_topics_buttons(topics, many_topics=False),
            )
            return

        await cb.message.answer(
            "Enter the target date for your goal (YYYY-MM-DD):",
            reply_markup=create_cancel_button(),
        )
        await state.set_state(GoalAddState.waiting_target_date)
        return

    elif cb.data.startswith("topic_"):
        topic_id = int(cb.data.split("_")[1])
        data_topic_id = data.get("topic_id")
        if topic_id == data_topic_id:
            await cb.message.answer(f"Topic with {topic_id} already chosen")
            return

        topic_map = data["topic_map"]
        title = topic_map.get(topic_id, str(topic_id))
        text = "Selected topic:\n" + f"\n• {title}"

        await state.update_data(topic_id=topic_id)
        await cb.message.answer(
            text, reply_markup=create_topics_buttons(topics, many_topics=False)
        )
        return
    else:
        await cb.message.answer("Wrong button. Please choose right one")
        return


@router.message(GoalAddState.waiting_target_date)
async def add_target_date(message: Message, state: FSMContext):
    try:
        datetime.strptime(message.text, "%Y-%m-%d").date()
    except ValueError:
        await message.answer(
            f"Wrong format. Please enter right date (YYYY-MM-DD)",
            reply_markup=create_cancel_button(),
        )
        return

    await state.update_data(target_date=message.text)
    await message.answer(
        "Enter target hours for your goal:", reply_markup=create_cancel_button()
    )
    await state.set_state(GoalAddState.waiting_target_hours)


@router.message(GoalAddState.waiting_target_hours)
async def add_target_hours(message: Message, state: FSMContext):
    try:
        target_hours = int(message.text)
    except ValueError:
        await message.answer(
            "Please enter integer number", reply_markup=create_cancel_button()
        )
        return

    await state.update_data(target_hours=target_hours)
    data = await state.get_data()
    token = data.pop("token")

    async with AsyncClient() as client:
        response = await client.post(
            API_URL, json=data, headers={"Authorization": f"Bearer {token}"}
        )

    await message.answer(f"{response.text}")
    await state.clear()
