from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from .keyboards import create_crud_reply_buttons
from .middleware import AuthMiddleware

API_GET_URL = "http://127.0.0.1:8000/token/{telegram_id}"
API_TOKEN_URL = "http://127.0.0.1:8000/auth/validate"

router = Router()
router.message.middleware(AuthMiddleware())

@router.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    await state.clear()

    await message.answer("Choose what you want to do:",
                         reply_markup=create_crud_reply_buttons())