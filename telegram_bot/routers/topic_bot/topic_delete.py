import os

from aiogram import types, F
from aiogram.types import CallbackQuery
from .topic_states import DeleteTopicState
from aiogram.fsm.context import FSMContext
from .topic_router import router
import httpx

from ...keyboards import create_cancel_button

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
API_URL = f"{API_BASE_URL}/topics/{{topic_id}}"


@router.callback_query(F.data == "delete_topic")
async def start_get(cb: CallbackQuery, state: FSMContext, token: str):
    await state.clear()
    await cb.answer()

    await state.update_data(token=token)
    await cb.message.answer(
        "Enter the id of topic:", reply_markup=create_cancel_button()
    )
    await state.set_state(DeleteTopicState.waiting_id)


@router.message(DeleteTopicState.waiting_id)
async def get_topic(message: types.Message, state: FSMContext):
    try:
        topic_id = int(message.text)
    except ValueError:
        await message.answer(
            "Enter a integer number", reply_markup=create_cancel_button()
        )
        return

    data = await state.get_data()
    token = data.pop("token")
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            API_URL.format(topic_id=topic_id),
            headers={"Authorization": f"Bearer {token}"},
        )

    if response.status_code == 200:
        await message.answer("Topic deleted successfully ✅")
    else:
        await message.answer(f"Error:{response.text}")
        await state.clear()
        return

    await state.clear()
