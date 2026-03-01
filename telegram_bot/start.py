from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import CallbackQuery

from .keyboards import create_start_buttons, create_entry_crud_buttons, create_topic_crud_buttons, create_auth_buttons
from .middleware import AuthMiddleware

API_GET_URL = "http://127.0.0.1:8000/token/{telegram_id}"
API_TOKEN_URL = "http://127.0.0.1:8000/auth/validate"

router = Router()
router.message.middleware(AuthMiddleware())
router.callback_query.middleware(AuthMiddleware())

@router.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    await state.clear()

    await message.answer("Choose what you want to do:",
                         reply_markup=create_start_buttons())

@router.callback_query(F.data == "entry_actions")
async def entry_actions(cb: CallbackQuery):
    await cb.answer()

    await cb.message.answer(
        "All entry actions:",
        reply_markup=create_entry_crud_buttons(),
    )

@router.callback_query(F.data == "topic_actions")
async def topic_actions(cb: CallbackQuery):
    await cb.answer()

    await cb.message.answer(
        "All topic actions:",
        reply_markup=create_topic_crud_buttons(),
    )