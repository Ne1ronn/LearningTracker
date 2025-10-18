from aiogram import Router, types
from aiogram.filters import Command
from typing import Any

router = Router(name=__name__)

@router.message(Command("start"))
async def start_handler(message: types.Message) -> Any:
    await message.answer('Hello from my router!')

@router.message(Command("Add entry"))
async def message_handler(message: types.Message) -> Any:
    await message.answer("Give me title of new entry")
    await title_handler()

async def is_string(message: types.Message) -> bool:
    return isinstance(message.text, str)

@router.message()
async def title_handler(message: types.Message) -> Any:
    if not is_string(message):
        await message.answer("This isn't a string")
    else:
        await message.answer("Now description of new entry")

