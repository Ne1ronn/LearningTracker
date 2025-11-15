from aiogram import Router, types
from aiogram.filters import Command

router = Router()

from . import entry_add
from . import entry_get
from . import entry_delete
from . import entry_update
from . import entry_patch

@router.message(Command("start_entry"))
async def start(message: types.Message):
    await message.answer("Hello, what do you want?\n"
                         "Add entry? Command /add_entry\n"
                         "To get? Command /get_entry?\n"
                         "To update? Command /update_entry\n"
                         "To update some attributes? Command /edit_entry\n"
                         "Or even delete? Command /delete_entry")