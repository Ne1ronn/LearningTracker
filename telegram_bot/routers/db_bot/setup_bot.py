from aiogram import Router, types
from aiogram.filters import Command
import httpx

router = Router()
API_URL = "http://127.0.0.1:8000/setup_database"

@router.message(Command("setup"))
async def setup_database(message: types.Message):
    async with httpx.AsyncClient() as client:
        response = await client.post(API_URL)

    if response.status_code == 200:
        await message.answer("Database created successfully✅")
    else:
        await message.answer(f"Error:{response.text}")