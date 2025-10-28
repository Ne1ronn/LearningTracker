from aiogram import Router, types
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
import httpx

router = Router()
API_URL = "http://127.0.0.1:8000/topic/{topic_id}"

class GetTopicState(StatesGroup):
    waiting_id = State()

@router.message(Command("get_topic"))
async def start_get(message: types.Message, state: FSMContext):
    await message.answer("Enter the id of topic:")
    await state.set_state(GetTopicState.waiting_id)

@router.message(GetTopicState.waiting_id)
async def get_topic(message: types.Message, state: FSMContext):
    try:
        topic_id = int(message.text)
        if not topic_id.is_integer():
            raise ValueError
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