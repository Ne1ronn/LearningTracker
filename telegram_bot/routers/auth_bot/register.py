import os

from aiogram import types, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from email_validator import validate_email, EmailNotValidError
from .auth_router import router
import httpx

from ...keyboards import create_cancel_button

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
API_GET_URL = f"{API_BASE_URL}/user/register/{{username}}"
API_EMAIL_URL = f"{API_BASE_URL}/userm/{{email}}"
API_POST_URL = f"{API_BASE_URL}/register"

class UserForm(StatesGroup):
    username = State()
    email = State()
    hashed_password = State()

@router.callback_query(F.data == "register")
async def register(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.answer()

    await cb.message.answer("Enter the username:", reply_markup=create_cancel_button())
    await state.set_state(UserForm.username)

@router.message(UserForm.username)
async def add_username(message: types.Message, state: FSMContext):
    async with httpx.AsyncClient() as client:
        response = await client.get(API_GET_URL.format(username=message.text))

    if response.status_code == 409:
        await message.answer("This username already exists. Enter another:", reply_markup=create_cancel_button())
        return

    await state.update_data(username=message.text)
    await message.answer("Enter the email:", reply_markup=create_cancel_button())
    await state.set_state(UserForm.email)

@router.message(UserForm.email)
async def add_email(message: types.Message, state: FSMContext):
    try:
        valid = validate_email(message.text)
        email = valid.email
    except EmailNotValidError:
        await message.answer("Incorrect email, try again:", reply_markup=create_cancel_button())
        return

    async with httpx.AsyncClient() as client:
        response = await client.get(API_EMAIL_URL.format(email=email))

    if response.status_code == 409:
        await message.answer("This email already exists. Enter another:", reply_markup=create_cancel_button())
        return

    await state.update_data(email=email)
    await message.answer("Enter the password:", reply_markup=create_cancel_button())
    await state.set_state(UserForm.hashed_password)

@router.message(UserForm.hashed_password)
async def add_password(message: types.Message, state: FSMContext):
    await state.update_data(password=message.text)
    data = await state.get_data()

    async with httpx.AsyncClient() as client:
        response = await client.post(API_POST_URL, json=data)

    if response.status_code == 201:
        await message.answer("User registered successfully")
    else:
        await message.answer(f"Error:{response.text}")
        await state.clear()
        return

    await state.clear()