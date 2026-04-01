import os
import httpx
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message
from telegram_bot.keyboards import (
    create_settings_buttons,
    create_timezone_buttons,
    create_true_false_buttons,
)
from telegram_bot.middleware import AuthMiddleware

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
API_GET_URL = f"{API_BASE_URL}/user"
API_TIMEZONE_URL = f"{API_BASE_URL}/user/timezone"
API_REMINDER_URL = f"{API_BASE_URL}/user/reminders"

router = Router()
router.message.middleware(AuthMiddleware())
router.callback_query.middleware(AuthMiddleware())


class SettingsState(StatesGroup):
    waiting_timezone = State()
    waiting_reminders = State()


@router.message(Command("settings"))
async def settings(message: Message, state: FSMContext, token: str):
    await state.clear()
    async with httpx.AsyncClient() as client:
        response = await client.get(
            API_GET_URL, headers={"Authorization": f"Bearer {token}"}
        )

    if response.status_code != 200:
        await message.answer(f"Error: {response.text}")
        await state.clear()
        return

    user_timezone = response.json().get("user_timezone")
    reminders_enabled = response.json().get("user_reminders_enabled")

    await message.answer(
        f"⚙️ <b>Your settings:</b>\n\n"
        f"🕐 Timezone: <code>{user_timezone or 'not set'}</code>\n"
        f"🔔 Reminders: {'✅ enabled' if reminders_enabled else '❌ disabled'}",
        reply_markup=create_settings_buttons(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "set_timezone")
async def ask_timezone(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await cb.message.answer(
        "Choose your timezone", reply_markup=create_timezone_buttons()
    )
    await state.set_state(SettingsState.waiting_timezone)


@router.callback_query(SettingsState.waiting_timezone)
async def set_timezone(cb: CallbackQuery, state: FSMContext, token: str):
    await cb.answer()

    if cb.data == "cancel":
        await state.clear()
        await cb.message.answer("Operation cancelled")
        return

    timezones = ["Asia/Almaty", "Europe/Moscow", "Asia/Bishkek", "Asia/Tashkent"]

    if cb.data not in timezones:
        await cb.message.answer("Invalid timezone")
        return

    timezone = cb.data

    async with httpx.AsyncClient() as client:
        response = await client.patch(
            API_TIMEZONE_URL,
            json={"timezone": timezone},
            headers={"Authorization": f"Bearer {token}"},
        )

        if response.status_code == 200:
            await cb.message.answer("Timezone successfully updated")
        else:
            await cb.message.answer(f"Error: {response.text}")

    await state.clear()


@router.callback_query(F.data == "set_reminders")
async def ask_reminders(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await cb.message.answer(
        "Choose enable or disable reminders", reply_markup=create_true_false_buttons()
    )
    await state.set_state(SettingsState.waiting_reminders)


@router.callback_query(SettingsState.waiting_reminders)
async def change_reminders(cb: CallbackQuery, state: FSMContext, token: str):
    await cb.answer()
    data = cb.data

    if data == "cancel":
        await state.clear()
        await cb.message.answer("Operation cancelled")
        return

    elif data == "true":
        reminders_enabled = True

    elif data == "false":
        reminders_enabled = False

    else:
        await cb.message.answer("Invalid button")
        return

    async with httpx.AsyncClient() as client:
        response = await client.patch(
            API_REMINDER_URL,
            json={"reminders_enabled": reminders_enabled},
            headers={"Authorization": f"Bearer {token}"},
        )

        if response.status_code == 200:
            await cb.message.answer("Reminders successfully updated")
        else:
            await cb.message.answer(f"Error: {response.text}")

    await state.clear()
