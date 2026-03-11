import os

from aiogram import types, F
from aiogram.types import CallbackQuery

from .topic_states import PatchTopicForm
from aiogram.fsm.context import FSMContext
from .topic_router import router
import httpx

from ...keyboards import create_topic_attribute_choose_buttons, create_yes_no_buttons, create_cancel_button

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
API_URL = f"{API_BASE_URL}/topics/{{topic_id}}"
API_ADMIN_URL = f"{API_BASE_URL}/auth/validate/admin"

@router.callback_query(F.data == "edit_topic")
async def start_patch(cb: CallbackQuery, state: FSMContext, token: str):
    await state.clear()
    await cb.answer()

    await cb.message.answer("Enter the id of topic:", reply_markup=create_cancel_button())
    await state.set_state(PatchTopicForm.waiting_id)

@router.message(PatchTopicForm.waiting_id)
async def get_topic(message: types.Message, state: FSMContext):
    try:
        topic_id = int(message.text)
    except ValueError:
        await message.answer("Enter a integer number", reply_markup=create_cancel_button())
        return

    async with httpx.AsyncClient() as client:
        response = await client.get(API_URL.format(topic_id=topic_id))

    if response.status_code != 200:
        await message.answer("Entered a wrong id, try again ❌", reply_markup=create_cancel_button())
        return

    await state.update_data(topic_id=topic_id, updates={})
    await message.answer("What exactly you want update?", reply_markup=create_topic_attribute_choose_buttons())
    await state.set_state(PatchTopicForm.waiting_attribute)

@router.callback_query(PatchTopicForm.waiting_attribute)
async def wait_attribute(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    attribute = cb.data

    if cb.data == "cancel":
        await state.clear()
        await cb.message.answer("Operation cancelled")
        return

    attributes = [
        "title",
        "skill",
        "description",
        "category",
        "is_active"
    ]

    if attribute not in attributes:
        await cb.message.answer("Invalid attribute", show_alert=True)
        return

    await state.update_data(current_attribute=attribute)
    await cb.message.answer("Enter a new value for attribute:", reply_markup=create_cancel_button())
    await state.set_state(PatchTopicForm.edit_attribute)

@router.message(PatchTopicForm.edit_attribute)
async def patch_topic(message: types.Message, state: FSMContext):
    data = await state.get_data()
    attribute = data["current_attribute"]
    updates = data["updates"]
    value = message.text.strip()

    updates[attribute] = value
    await state.update_data(updates=updates)

    await message.answer("Field added to changes\n"
                         "Would you update anything else?)",
                         reply_markup=create_yes_no_buttons("field"))
    await state.set_state(PatchTopicForm.waiting_confirm)

@router.callback_query(PatchTopicForm.waiting_confirm)
async def confirm(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    if cb.data == "yes_field":
        await cb.message.answer("What exactly you want update?", reply_markup=create_topic_attribute_choose_buttons())
        await state.set_state(PatchTopicForm.waiting_attribute)
        return

    data = await state.get_data()
    topic_id = data["topic_id"]
    updates = data["updates"]
    token = data.pop("token")

    async with httpx.AsyncClient() as client:
        response = await client.patch(API_URL.format(topic_id=topic_id), json=updates, headers={"Authorization": f"Bearer {token}"})

    if response.status_code == 200:
        await cb.message.answer("Topic successfully updated ✅")
    else:
        await cb.message.answer(f"Error:{response.text}")
        await state.clear()
        return

    await state.clear()