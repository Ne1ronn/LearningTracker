from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import CallbackQuery
from telegram_bot.middleware import AuthMiddleware

router = Router()
router.message.middleware(AuthMiddleware())
router.callback_query.middleware(AuthMiddleware())


@router.message(Command("cancel"))
async def cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Operation cancelled")


@router.callback_query(F.data == "cancel")
async def cancel_button(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await cb.message.answer("Operation cancelled")
    await state.clear()
