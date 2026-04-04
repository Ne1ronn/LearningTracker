import os
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from httpx import AsyncClient
from .goal_router import router
from .goal_states import GoalStatsState
from ...keyboards import create_cancel_button

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
API_URL = f"{API_BASE_URL}/goals/{{goal_id}}/stats"
API_TOPIC_URL = f"{API_BASE_URL}/topics/{{topic_id}}"


@router.callback_query(F.data == "goal_stats")
async def get_goal_id(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.clear()

    await cb.message.answer(
        "Enter id of your goal:", reply_markup=create_cancel_button()
    )
    await state.set_state(GoalStatsState.waiting_id)


@router.message(GoalStatsState.waiting_id)
async def get_goal_stats(message: Message, state: FSMContext, token: str):
    try:
        goal_id = int(message.text)
    except ValueError:
        await message.answer(
            "Please enter integer number", reply_markup=create_cancel_button()
        )
        return

    async with AsyncClient() as client:
        goal_response = await client.get(
            API_URL.format(goal_id=goal_id),
            headers={"Authorization": f"Bearer {token}"},
        )

        if goal_response.status_code == 200:
            goal_data = goal_response.json()
            status = goal_data.get("status")
            topic_id = goal_data.get("topic_id")
            topic_response = await client.get(
                API_TOPIC_URL.format(topic_id=topic_id),
                headers={"Authorization": f"Bearer {token}"},
            )

            topic_title = (
                topic_response.json().get("title")
                if topic_response.status_code == 200
                else "—"
            )
            status_emoji = {
                "completed": "✅",
                "overdue": "❌",
                "on_track": "🟢",
                "behind": "🔴",
            }.get(status, "❓")

            text = (
                f"{status_emoji} <b>{topic_title}</b>\n"
                f"\n"
                f"📊 Status: <b>{status}</b>\n"
                f"\n"
                f"⏱ Done: <b>{goal_data.get('hours_done') or 0}h</b>  "
                f"🎯 Target: <b>{goal_data.get('target_hours') or 0}h</b>  "
                f"⏳ Left: <b>{goal_data.get('hours_left') or 0}h</b>\n"
                f"\n"
                f"📅 Days left: <b>{goal_data.get('days_left') or 0}</b>\n"
                f"🚀 Current tempo: <b>{(goal_data.get('current_tempo') or 0):.1f}h/day</b>\n"
            )

            if status == "behind":
                text += f"⚡️ Needed tempo: <b>{goal_data.get('needed_tempo', 0):.1f}h/day</b>\n"

            await message.answer(text, parse_mode="HTML")

        else:
            await message.answer(f"Error: {goal_response.text}")
            await state.clear()
            return

    await state.clear()
