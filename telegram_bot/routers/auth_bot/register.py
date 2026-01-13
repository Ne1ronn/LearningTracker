from aiogram import Router, types
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from email_validator import validate_email, EmailNotValidError
from .auth_router import router
import httpx

API_GET_URL = "http://127.0.0.1:8000/user/register/{username}"
API_EMAIL_URL = "http://127.0.0.1:8000/userm/{email}"
API_POST_URL = "http://127.0.0.1:8000/register"

class UserForm(StatesGroup):
    username = State()
    email = State()
    hashed_password = State()

@router.message(Command("register"))
async def register(message: types.Message, state: FSMContext):
    await message.answer("Enter the username:")
    await state.set_state(UserForm.username)

@router.message(UserForm.username)
async def add_username(message: types.Message, state: FSMContext):
    async with httpx.AsyncClient() as client:
        response = await client.get(API_GET_URL.format(username=message.text))

    if response.status_code == 409:
        await message.answer("This username already exists. Enter another:")
        return

    await state.update_data(username=message.text)
    await message.answer("Enter the email:")
    await state.set_state(UserForm.email)

@router.message(UserForm.email)
async def add_email(message: types.Message, state: FSMContext):
    try:
        valid = validate_email(message.text)
        email = valid.email
    except EmailNotValidError:
        await message.answer("Incorrect email, try again:")
        return

    async with httpx.AsyncClient() as client:
        response = await client.get(API_EMAIL_URL.format(email=email))

    if response.status_code == 409:
        await message.answer("This email already exists. Enter another:")
        return

    await state.update_data(email=email)
    await message.answer("Enter the password:")
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