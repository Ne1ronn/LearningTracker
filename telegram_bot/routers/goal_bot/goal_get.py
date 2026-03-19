import os
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from httpx import AsyncClient
from .goal_router import router
from .goal_states import GoalGetState
from ...keyboards import create_cancel_button

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
API_ID_URL = f"{API_BASE_URL}/goals/{{goal_id}}"
API_URL = f"{API_BASE_URL}/goals"
API_TOPIC_URL = f"{API_BASE_URL}/topics/{{topic_id}}"


@router.callback_query(F.data == "get_goal")
async def get_goal_id(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.clear()

    await cb.message.answer(
        "Enter id of your goal:", reply_markup=create_cancel_button()
    )
    await state.set_state(GoalGetState.waiting_id)


@router.message(GoalGetState.waiting_id)
async def get_goal(message: Message, state: FSMContext, token: str):
    try:
        goal_id = int(message.text)
    except ValueError:
        await message.answer(
            "Please enter integer number", reply_markup=create_cancel_button()
        )
        return

    async with AsyncClient() as client:
        goal_response = await client.get(
            API_ID_URL.format(goal_id=goal_id),
            headers={"Authorization": f"Bearer {token}"},
        )

        if goal_response.status_code == 200:
            goal_data = goal_response.json()
            topic_id = goal_data.get("topic_id")
            topic_response = await client.get(
                API_TOPIC_URL.format(topic_id=topic_id),
                headers={"Authorization": f"Bearer {token}"},
            )

            if topic_response.status_code == 200:
                topic_title = topic_response.json().get("title")

                started = (
                    goal_data["started_at"][:10] if goal_data["started_at"] else "—"
                )
                deadline = goal_data["target_date"] if goal_data["target_date"] else "—"
                title = topic_title or "—"

                text = (
                    f"🎯 <b>{title}</b>\n"
                    f"\n"
                    f"📅 Start: <b>{started}</b>\n"
                    f"🏁 Deadline: <b>{deadline}</b>\n"
                    f"\n"
                    f"⏱ Target hours: <b>{goal_data['target_hours']}ч</b>\n"
                    f"🆔 <code>{goal_data['id']}</code>"
                )

                await message.answer(text, parse_mode="HTML")

            else:
                await message.answer(f"Error: {topic_response.text}")
                await state.clear()
                return

        else:
            await message.answer(f"Error: {goal_response.text}")
            await state.clear()
            return

        await state.clear()


@router.callback_query(F.data == "get_goals")
async def get_goals(cb: CallbackQuery, state: FSMContext, token: str):
    await cb.answer()
    await state.clear()

    async with AsyncClient() as client:
        response = await client.get(
            API_URL, headers={"Authorization": f"Bearer {token}"}
        )

        if response.status_code == 200:
            goals = response.json()

            if not goals:
                await cb.message.answer("You don't have any goals.")
                await state.clear()
                return

            for goal_data in goals:
                topic_id = goal_data.get("topic_id")
                topic_response = await client.get(
                    API_TOPIC_URL.format(topic_id=topic_id),
                    headers={"Authorization": f"Bearer {token}"},
                )

                if topic_response.status_code == 200:
                    topic_title = topic_response.json().get("title")

                    started = (
                        goal_data["started_at"][:10] if goal_data["started_at"] else "—"
                    )
                    deadline = (
                        goal_data["target_date"] if goal_data["target_date"] else "—"
                    )

                    text = (
                        f"🎯 <b>{topic_title or '—'}</b>\n"
                        f"\n"
                        f"📅 Start: <b>{started}</b>\n"
                        f"🏁 Deadline: <b>{deadline}</b>\n"
                        f"\n"
                        f"⏱ Target hours: <b>{goal_data['target_hours']}ч</b>\n"
                        f"🆔 <code>{goal_data['id']}</code>"
                    )

                    await cb.message.answer(text, parse_mode="HTML")

                else:
                    await cb.message.answer(f"Error: {topic_response.text}")
                    await state.clear()
                    return

        else:
            await cb.message.answer(f"Error: {response.text}")
            await state.clear()
            return

    await state.clear()
