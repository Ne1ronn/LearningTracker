from aiogram import Router, types
from aiogram.filters import Command

router = Router()

from . import login
from . import register

@router.message(Command("start_auth"))
async def start(message: types.Message):
    await message.answer("Hello, what do you want?\n"
                         "To register? Command /register\n"
                         "To login? Command /login\n")