from aiogram import Router, types
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from .topic_router import router
import httpx

API_URL = "http://127.0.0.1:8000/topic/{topic_id}"

class DeleteTopicState(StatesGroup):
    waiting_id = State()

@router.message(Command("delete_topic"))
async def start_get(message: types.Message, state: FSMContext):
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

    async with httpx.AsyncClient() as client:
        response = await client.delete(API_URL.format(topic_id=topic_id))

    if response.status_code == 200:
        await message.answer("Topic deleted successfully ✅")
    else:
        await message.answer(f"Error:{response.text}")

    await state.clear()