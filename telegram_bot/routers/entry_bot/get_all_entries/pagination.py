from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from ..entry_router import router
from .entry_get_all import show_page

@router.callback_query(F.data == "previous")
async def previous_page(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    data = await state.get_data()
    offset = max(0, data["offset"] - data["limit"])
    await state.update_data(offset=offset)
    token = data["token"]
    await show_page(state, cb.message, token)

@router.callback_query(F.data == "next")
async def next_page(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    data = await state.get_data()
    offset = data["offset"] + data["limit"]

    if offset >= data["total"]:
        return

    await state.update_data(offset=offset)
    token = data["token"]
    await show_page(state, cb.message, token)