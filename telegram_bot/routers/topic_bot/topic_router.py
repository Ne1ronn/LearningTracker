from aiogram import Router, types
from aiogram.filters import Command

router = Router()

from . import topic_add
from . import topic_get
from . import topic_delete
from . import topic_update
from . import topic_patch

@router.message(Command("start_topic"))
async def start(message: types.Message):
    await message.answer("Hello, what do you want?\n"
                         "Add topic? Command /add_topic\n"
                         "To get? Command /get_topic\n"
                         "To update? Command /update_topic\n"
                         "To update some attributes? Command /patch_topic\n"
                         "Or even delete? Command /delete_topic")