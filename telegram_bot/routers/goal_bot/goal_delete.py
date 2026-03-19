import os
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from httpx import AsyncClient
from .goal_router import router
from .goal_states import GoalDeleteState
from ...keyboards import (
    create_cancel_button,
)

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
API_URL = f"{API_BASE_URL}/goals/{{goal_id}}"


@router.callback_query(F.data == "delete_goal")
async def get_goal_id(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.clear()

    await cb.message.answer(
        "Enter id of your goal:", reply_markup=create_cancel_button()
    )
    await state.set_state(GoalDeleteState.waiting_id)


@router.message(GoalDeleteState.waiting_id)
async def delete_goal(message: Message, state: FSMContext, token: str):
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
            delete_response = await client.delete(
                API_URL.format(goal_id=goal_id),
                headers={"Authorization": f"Bearer {token}"},
            )

            await message.answer(f"{delete_response.text}")
        else:
            await message.answer(f"Error: {goal_response.text}")

    await state.clear()
