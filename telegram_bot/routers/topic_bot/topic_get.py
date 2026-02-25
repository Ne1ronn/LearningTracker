from aiogram import types, F
from aiogram.types import CallbackQuery
from .topic_states import GetTopicState
from aiogram.fsm.context import FSMContext
from .topic_router import router
import httpx

API_URL = "http://127.0.0.1:8000/topic/{topic_id}"

@router.callback_query(F.data == "get_topic")
async def start_get(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.answer()

    await cb.message.answer("Enter the id of topic:")
    await state.set_state(GetTopicState.waiting_id)

@router.message(GetTopicState.waiting_id)
async def get_topic(message: types.Message, state: FSMContext):
    try:
        topic_id = int(message.text)
    except ValueError:
        await message.answer("Enter a integer number")
        return

    async with httpx.AsyncClient() as client:
        response = await client.get(API_URL.format(topic_id=topic_id))

    if response.status_code == 200:
        data = response.json()
        await message.answer(
            f"Your topic data: \n"
            f"Topic id: {data['id']}\n"
            f"Topic title: {data['title']}\n"
            f"Topic skill: {data['skill']}\n"
            f"Topic need: {data['need']}\n"
            f"Topic progress_score: {data['progress_score']}\n"
            f"Topic is_active: {data['is_active']}")
    else:
        await message.answer(f"Error:{response.text}")

    await state.clear()