from aiogram import F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from telegram_bot.keyboards import create_choose_buttons, create_page_buttons
from ..entry_router import router
import httpx

API_ALL_URL = "http://127.0.0.1:8000/entries/page"
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
    token = data["token"]
    await state.update_data(limit=5, offset=0)
    await show_page(state, cb.message, token)

async def show_page(state: FSMContext, message: types.Message, token: str):
    data = await state.get_data()
    limit = data["limit"]
    offset = data["offset"]

    params = {k: v for k, v in data.items() if v is not None and k not in ["token", "limit", "offset", "total"]}
    params["limit"] = limit
    params["offset"] = offset

    async with httpx.AsyncClient() as client:
        response = await client.get(API_ALL_URL, headers={"Authorization": f"Bearer {token}"}, params=params)

    if response.status_code == 200:
        entries = response.json().get("entries")
        total = response.json().get("total")
        next_offset = offset + limit

        await state.update_data(total=total)

        for entry in entries:
            private_emoji = "🔒" if entry['private'] else "🌐"
            mood_emoji = "😄" if entry['mood_score'] >= 8 else "😐" if entry['mood_score'] == 5 else "😔"

            text = (
                f"{private_emoji} <b>{entry['title']}</b>\n"
                f"\n"
                f"📝 {entry['description']}\n"
                f"\n"
                f"🏷 <i>{entry['tags'] if entry['tags'] else 'no tags'}</i>\n"
                f"\n"
                f"{mood_emoji} Mood: <b>{entry['mood_score']}/10</b>  "
                f"⭐️ Progress: <b>{entry['progress_score']}/10</b>  "
                f"⏱ <b>{entry['learning_hours']}ч</b>\n"
                f"🆔 <code>{entry['id']}</code>"
            )

            await message.answer(text, parse_mode="HTML")

        await state.update_data(token=token)
        await message.answer(
            f"Page {offset}-{min(next_offset, total)} of {total}",
            reply_markup=create_page_buttons(offset, limit, total)
        )

        await message.answer(
            "Want to enhance filtering and sorting?",
            reply_markup=create_choose_buttons()
        )
    else:
        await message.answer(f"Error: {response.text}")
        await state.clear()
        return