import os
from datetime import datetime
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from httpx import AsyncClient
from .goal_router import router
from .goal_states import GoalPatchState
from ...keyboards import (
    create_cancel_button,
    create_goal_attribute_choose_buttons,
    create_yes_no_buttons,
)

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
API_URL = f"{API_BASE_URL}/goals/{{goal_id}}"
API_TOPICS_URL = f"{API_BASE_URL}/topics"


@router.callback_query(F.data == "patch_goal")
async def get_goal_id(cb: CallbackQuery, state: FSMContext, token: str):
    await cb.answer()
    await state.clear()

    await state.update_data(token=token)
    await cb.message.answer(
        "Enter id of your goal:", reply_markup=create_cancel_button()
    )
    await state.set_state(GoalPatchState.waiting_id)


@router.message(GoalPatchState.waiting_id)
async def get_goal(message: Message, state: FSMContext):
    try:
        goal_id = int(message.text)
    except ValueError:
        await message.answer(
            "Please enter integer number", reply_markup=create_cancel_button()
        )
        return

    data = await state.get_data()
    token = data.get("token")
    async with AsyncClient() as client:
        goal_response = await client.get(
            API_URL.format(goal_id=goal_id),
            headers={"Authorization": f"Bearer {token}"},
        )

        if goal_response.status_code == 200:
            await state.update_data(goal_id=goal_id, updates={})
            await message.answer(
                "What exactly you want update?",
                reply_markup=create_goal_attribute_choose_buttons(),
            )
            await state.set_state(GoalPatchState.waiting_attribute)
        else:
            await message.answer(f"Error: {goal_response.text}")


@router.callback_query(GoalPatchState.waiting_attribute)
async def get_attribute(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    attribute = cb.data
    if cb.data == "cancel":
        await state.clear()
        await cb.message.answer("Operation cancelled")
        return

    attributes = ["target_date", "target_hours"]

    if attribute not in attributes:
        await cb.answer("Invalid attribute", show_alert=True)
        return

    await state.update_data(current_attribute=attribute)

    await cb.message.answer(
        "Enter a new value for attribute:", reply_markup=create_cancel_button()
    )
    await state.set_state(GoalPatchState.edit_attribute)


@router.message(GoalPatchState.edit_attribute)
async def edit_attribute(message: Message, state: FSMContext):
    data = await state.get_data()
    attribute = data["current_attribute"]
    updates = data["updates"]
    value = message.text.strip()

    if attribute == "target_date":
        try:
            value = datetime.strptime(message.text, "%Y-%m-%d").date()
        except ValueError:
            await message.answer(
                f"Wrong format. Please enter right date (YYYY-MM-DD)",
                reply_markup=create_cancel_button(),
            )
            return

    elif attribute == "target_hours":
        try:
            value = int(message.text)
        except ValueError:
            await message.answer(
                "Please enter integer number", reply_markup=create_cancel_button()
            )
            return

    updates[attribute] = value
    await state.update_data(updates=updates)

    await message.answer(
        "Field added to changes\n" "Would you update anything else?",
        reply_markup=create_yes_no_buttons("field"),
    )
    await state.set_state(GoalPatchState.waiting_confirm)


@router.callback_query(GoalPatchState.waiting_confirm)
async def patch_goal(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    if cb.data == "yes_field":
        await cb.message.answer(
            "What exactly you want update?",
            reply_markup=create_goal_attribute_choose_buttons(),
        )
        await state.set_state(GoalPatchState.waiting_attribute)
        return

    data = await state.get_data()
    goal_id = data["goal_id"]
    updates = data["updates"]
    token = data.pop("token")

    async with AsyncClient() as client:
        goal_response = await client.patch(
            API_URL.format(goal_id=goal_id),
            json=updates,
            headers={"Authorization": f"Bearer {token}"},
        )

    await cb.message.answer(f"{goal_response.text}")
    await state.clear()
