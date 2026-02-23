from aiogram import types, F
from aiogram.types import CallbackQuery

from .topic_states import UpdateTopicForm
from aiogram.fsm.context import FSMContext
from .topic_router import router
import httpx

API_URL = "http://127.0.0.1:8000/topic/{topic_id}"
API_ADMIN_URL = "http://127.0.0.1:8000/auth/validate/admin"

@router.callback_query(F.data == "update_entry")
async def start_update(cb: CallbackQuery, state: FSMContext, token: str):
    await state.clear()
    await cb.answer()

    async with httpx.AsyncClient() as client:
        response = await client.get(API_ADMIN_URL, headers={"Authorization": f"Bearer {token}"})

    if response.status_code != 200:
        await cb.message.answer("You don't have enough permissions")
        await state.clear()
        return

    await state.update_data(token=token)

    await cb.message.answer("Enter the id of topic:")
    await state.set_state(UpdateTopicForm.waiting_id)

@router.message(UpdateTopicForm.waiting_id)
async def update_topic(message: types.Message, state: FSMContext):
    try:
        topic_id = int(message.text)
        if not topic_id.is_integer():
            raise ValueError
    except ValueError:
        await message.answer("Enter a integer number")
        return

    async with httpx.AsyncClient() as client:
        response = await client.get(API_URL.format(topic_id=topic_id))

    if response.status_code != 200:
        await message.answer("Entered a wrong id, try again ❌")
        return

    await state.update_data(topic_id=topic_id)
    await message.answer("Enter the title of updated topic:")
    await state.set_state(UpdateTopicForm.title)

@router.message(UpdateTopicForm.title)
async def add_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Now the skill of topic:")
    await state.set_state(UpdateTopicForm.skill)

@router.message(UpdateTopicForm.skill)
async def add_skill(message: types.Message, state: FSMContext):
    await state.update_data(skill=message.text)
    await message.answer("Now the need of topic:")
    await state.set_state(UpdateTopicForm.need)

@router.message(UpdateTopicForm.need)
async def add_need(message: types.Message, state: FSMContext):
    try:
        score = int(message.text)
        if not (0 <= score <= 10):
            raise ValueError
    except ValueError:
        await message.answer("Enter number between 0 and 10")
        return
    await state.update_data(need=score)
    await message.answer("Now the progress score of topic:")
    await state.set_state(UpdateTopicForm.progress_score)

@router.message(UpdateTopicForm.progress_score)
async def add_score(message: types.Message, state: FSMContext):
    try:
        score = int(message.text)
        if not (0 <= score <= 10):
            raise ValueError
    except ValueError:
        await message.answer("Enter number between 0 and 10")
        return

    await state.update_data(progress_score=score)

    data = await state.get_data()
    topic_id = data.pop('topic_id')
    token = data.pop("token")

    async with httpx.AsyncClient() as client:
        response = await client.put(API_URL.format(topic_id=topic_id), json=data, headers={"Authorization": f"Bearer {token}"})

    if response.status_code == 200:
        await message.answer("Topic successfully updated ✅")
    else:
        await message.answer(f"Error:{response.text}")