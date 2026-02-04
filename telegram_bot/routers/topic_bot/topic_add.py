from aiogram import types
from aiogram.fsm.context import FSMContext
from .topic_states import TopicForm
from aiogram.filters import Command
from .topic_router import router
import httpx

API_URL = "http://127.0.0.1:8000/topics"
API_GET_URL = "http://127.0.0.1:8000/token/{telegram_id}"
API_TOKEN_URL = "http://127.0.0.1:8000/auth/validate"
API_ADMIN_URL = "http://127.0.0.1:8000/auth/validate/admin"

@router.message(Command("add_topic"))
async def start_topic(message: types.Message, state: FSMContext):
    telegram_id = message.from_user.id
    async with httpx.AsyncClient() as client:
        response = await client.get(API_GET_URL.format(telegram_id=telegram_id))

    if response.status_code != 200:
        await message.answer(f"User with telegram id {telegram_id} unauthorized. Use command /login for authorize")
        await state.clear()
        return

    token = response.json().get("access_token")

    async with httpx.AsyncClient() as client:
        response = await client.get(API_TOKEN_URL, headers={"Authorization": f"Bearer {token}"})

    if response.status_code != 200:
        await message.answer(f"User didn't authorize. Use command /login for authorize")
        await state.clear()
        return

    async with httpx.AsyncClient() as client:
        response = await client.get(API_ADMIN_URL, headers={"Authorization": f"Bearer {token}"})

    if response.status_code != 200:
        await message.answer("You don't have enough permissions")
        await state.clear()
        return

    await state.update_data(token=token)
    await message.answer("Enter the title of new topic:")
    await state.set_state(TopicForm.title)

@router.message(TopicForm.title)
async def add_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Now the skill of topic:")
    await state.set_state(TopicForm.skill)

@router.message(TopicForm.skill)
async def add_skill(message: types.Message, state: FSMContext):
    await state.update_data(skill=message.text)
    await message.answer("Now the need of topic:")
    await state.set_state(TopicForm.need)

@router.message(TopicForm.need)
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
    await state.set_state(TopicForm.progress_score)

@router.message(TopicForm.progress_score)
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
    token = data.pop("token")
    async with httpx.AsyncClient() as client:
        response = await client.post(API_URL, json=data, headers={"Authorization": f"Bearer {token}"})

    if response.status_code == 201:
        await message.answer(response.text+"✅")
    else:
        await message.answer(f"Error:{response.text}")

    await state.clear()