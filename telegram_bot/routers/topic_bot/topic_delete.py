from aiogram import types
from .topic_states import DeleteTopicState
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from .topic_router import router
import httpx

API_URL = "http://127.0.0.1:8000/topic/{topic_id}"
API_GET_URL = "http://127.0.0.1:8000/token/{telegram_id}"
API_TOKEN_URL = "http://127.0.0.1:8000/auth/validate"

@router.message(Command("delete_topic"))
async def start_get(message: types.Message, state: FSMContext):
    await state.clear()
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

    await state.update_data(token=token)

    await message.answer("Enter the id of topic:")
    await state.set_state(DeleteTopicState.waiting_id)

@router.message(DeleteTopicState.waiting_id)
async def get_topic(message: types.Message, state: FSMContext):
    try:
        topic_id = int(message.text)
        if not topic_id.is_integer():
            raise ValueError
    except ValueError:
        await message.answer("Enter a integer number")
        return

    data = await state.get_data()
    token = data.pop("token")
    async with httpx.AsyncClient() as client:
        response = await client.delete(API_URL.format(topic_id=topic_id), headers={"Authorization": f"Bearer {token}"})

    if response.status_code == 200:
        await message.answer("Topic deleted successfully ✅")
    else:
        await message.answer(f"Error:{response.text}")

    await state.clear()