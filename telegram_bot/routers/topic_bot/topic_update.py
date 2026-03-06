from aiogram import types, F
from aiogram.types import CallbackQuery

from .topic_states import UpdateTopicForm
from aiogram.fsm.context import FSMContext
from .topic_router import router
import httpx

from ...keyboards import create_cancel_button

API_URL = "http://127.0.0.1:8000/topic/{topic_id}"
API_ADMIN_URL = "http://127.0.0.1:8000/auth/validate/admin"

@router.callback_query(F.data == "update_topic")
async def start_update(cb: CallbackQuery, state: FSMContext, token: str):
    await state.clear()
    await cb.answer()

    await state.update_data(token=token)
    await cb.message.answer("Enter the id of topic:", reply_markup=create_cancel_button())
    await state.set_state(UpdateTopicForm.waiting_id)

@router.message(UpdateTopicForm.waiting_id)
async def update_topic(message: types.Message, state: FSMContext):
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

    await state.update_data(topic_id=topic_id)
    await message.answer("Enter the title of updated topic:", reply_markup=create_cancel_button())
    await state.set_state(UpdateTopicForm.title)

@router.message(UpdateTopicForm.title)
async def add_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Now the skill of topic:", reply_markup=create_cancel_button())
    await state.set_state(UpdateTopicForm.skill)

@router.message(UpdateTopicForm.skill)
async def add_skill(message: types.Message, state: FSMContext):
    await state.update_data(skill=message.text)
    await message.answer("Now the description of topic:", reply_markup=create_cancel_button())
    await state.set_state(UpdateTopicForm.description)

@router.message(UpdateTopicForm.description)
async def add_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Now the category of topic:", reply_markup=create_cancel_button())
    await state.set_state(UpdateTopicForm.category)

@router.message(UpdateTopicForm.category)
async def add_category(message: types.Message, state: FSMContext):
    await state.update_data(category=message.text)

    data = await state.get_data()
    topic_id = data.pop('topic_id')
    token = data.pop("token")

    async with httpx.AsyncClient() as client:
        response = await client.put(API_URL.format(topic_id=topic_id), json=data, headers={"Authorization": f"Bearer {token}"})

    if response.status_code == 200:
        await message.answer("Topic successfully updated ✅")
    else:
        await message.answer(f"Error:{response.text}")
        await state.clear()
        return