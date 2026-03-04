from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from telegram_bot.keyboards import create_choose_buttons
from ..entry_router import router
import httpx

API_ALL_URL = "http://127.0.0.1:8000/entries"
API_GET_URL = "http://127.0.0.1:8000/token/{telegram_id}"
API_TOKEN_URL = "http://127.0.0.1:8000/auth/validate"

@router.callback_query(F.data == "get_all_entries")
async def get_all_entries(cb: CallbackQuery, state: FSMContext, token: str):
    await state.clear()
    await cb.answer()

    await state.update_data({
        "token": token,
        "private": None,
        "target_date": None,
        "min_mood_score": None,
        "max_mood_score": None,
        "min_progress_score": None,
        "max_progress_score": None,
        "min_learning_hours": None,
        "max_learning_hours": None,
        "sort": None,
    })

    await cb.message.answer(
        f"Choose the sorting or filtering of result, or show the result:",
        reply_markup=create_choose_buttons(),
    )

@router.callback_query(F.data == "show_result")
async def show_result(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    token = data.pop("token")

    params = {}
    for key, value in data.items():
        if value is not None:
            params[key] = value

    async with httpx.AsyncClient() as client:
        response = await client.get(API_ALL_URL, headers={"Authorization": f"Bearer {token}"}, params=params)

    if response.status_code == 200:
        data = response.json()

        for entry in data:
            await cb.message.answer(
                f"Your entry data:\n"
                f"Entry id: {entry['id']}\n"
                f"Entry title: {entry['title']}\n"
                f"Entry description: {entry['description']}\n"
                f"Entry tags: {entry['tags']}\n"
                f"Entry mood_score: {entry['mood_score']}\n"
                f"Entry progress_score: {entry['progress_score']}\n"
                f"Entry learning_hours: {entry['learning_hours']}\n"
                f"Entry private: {entry['private']}"
            )
    else:
        await cb.message.answer(f"Error: {response.text}")
        await state.clear()
        return

    await state.update_data(token=token)
    await cb.message.answer(
        "Want to enhance filtering and sorting?",
        reply_markup=create_choose_buttons()
    )
    await cb.answer()