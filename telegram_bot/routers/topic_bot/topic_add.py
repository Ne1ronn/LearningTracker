import os

from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from .topic_states import TopicForm
from .topic_router import router
import httpx

from ...keyboards import create_cancel_button

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
API_URL = f"{API_BASE_URL}/topics"

@router.callback_query(F.data == "add_topic")
async def start_topic(cb: CallbackQuery, state: FSMContext, token: str):
    await state.clear()
    await cb.answer()

    await state.update_data(token=token)
    await cb.message.answer("Enter the title of new topic:", reply_markup=create_cancel_button())
    await state.set_state(TopicForm.title)

@router.message(TopicForm.title)
async def add_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Now the skill of topic:", reply_markup=create_cancel_button())
    await state.set_state(TopicForm.skill)

@router.message(TopicForm.skill)
async def add_skill(message: types.Message, state: FSMContext):
    await state.update_data(skill=message.text)
    await message.answer("Now the description of topic:", reply_markup=create_cancel_button())
    await state.set_state(TopicForm.description)

@router.message(TopicForm.description)
async def add_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Now the category of topic:", reply_markup=create_cancel_button())
    await state.set_state(TopicForm.category)

@router.message(TopicForm.category)
async def add_category(message: types.Message, state: FSMContext):
    await state.update_data(category=message.text)
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