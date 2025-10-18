from aiogram import Router, types
from aiogram.filters import Command
from typing import Any

my_router = Router(name=__name__)

@my_router.message(Command("start"))
async def start_handler(message: types.Message) -> Any:
    await message.answer('Hello from my router!')