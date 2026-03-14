import os
from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from httpx import AsyncClient
from .middleware import AuthMiddleware

router = Router()
router.message.middleware(AuthMiddleware())

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
API_URL = f"{API_BASE_URL}/profile/stats"


@router.message(Command("/profile"))
async def profile(message: types.Message, state: FSMContext, token: str):
    await state.clear()
    async with AsyncClient() as client:
        response = await client.get(
            API_URL, headers={"Authorization": f"Bearer {token}"}
        )

    if response.status_code != 200:
        await message.answer(f"Error: {response.text}")
        await state.clear()
        return

    data = response.json()
    text = (
        "📊 <b>Your Profile</b>\n\n"
        f"⏱ Total hours: <b>{data['total_hours_all_time']}</b>\n"
        f"📅 Average per day: <b>{data['average_hours_all_time']}</b>\n\n"
        f"🏆 Favorite topic: <b>{data['favorite_topic']}</b>\n"
        f"⏳ Hours on it: <b>{data['favorite_topic_hours']}</b>\n\n"
        f"🔥 Current streak: <b>{data['current_streak']} days</b>\n"
        f"🎯 Max streak: <b>{data['max_streak']} days</b>\n"
    )
    await message.answer(text, parse_mode="HTML")
