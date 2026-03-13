import os

from aiogram import types, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from .auth_router import router
import httpx

from ...keyboards import create_cancel_button

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
API_URL = f"{API_BASE_URL}/login"
API_GET_URL = f"{API_BASE_URL}/user/login/{{username}}"
API_POST_URL = f"{API_BASE_URL}/token"
BOT_SECRET = os.getenv("BOT_SECRET")


class UserLoginForm(StatesGroup):
    username = State()
    password = State()


@router.callback_query(F.data == "login")
async def wait_username(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.answer()

    await cb.message.answer(
        "Enter the username of your user:", reply_markup=create_cancel_button()
    )
    await state.set_state(UserLoginForm.username)


@router.message(UserLoginForm.username)
async def check_username(message: types.Message, state: FSMContext):
    await state.update_data(telegram_id=message.from_user.id)
    async with httpx.AsyncClient() as client:
        response = await client.get(API_GET_URL.format(username=message.text))

    if response.status_code == 404:
        await message.answer(f"{response.text}")
        await state.clear()
        return

    await message.answer("Enter the password:", reply_markup=create_cancel_button())
    await state.update_data(username=message.text)
    await state.set_state(UserLoginForm.password)


@router.message(UserLoginForm.password)
async def check_password(message: types.Message, state: FSMContext):
    data = await state.get_data()
    username = data.pop("username")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            API_URL, data={"username": username, "password": message.text}
        )

    if response.status_code == 200:
        await state.update_data(
            access_token=response.json().get("access_token"),
            refresh_token=response.json().get("refresh_token"),
        )
        await message.answer("User login successfully")
        await add_token(message, state)
    else:
        await message.answer(f"Error:{response.text}")
        await state.clear()
        return


async def add_token(message: types.Message, state: FSMContext):
    data = await state.get_data()
    access_token = data.pop("access_token")
    refresh_token = data.pop("refresh_token")
    telegram_id = data.pop("telegram_id")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            API_POST_URL,
            params={"telegram_id": telegram_id},
            json={"token": refresh_token},
            headers={
                "Authorization": f"Bearer {access_token}",
                "X-Bot-Secret": BOT_SECRET,
            },
        )

    if response.status_code != 201:
        await message.answer(f"{response.text}")
        await state.clear()
        return

    await state.clear()
