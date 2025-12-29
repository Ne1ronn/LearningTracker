from aiogram import Router, types
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from .auth_router import router
import httpx

API_URL = "http://127.0.0.1:8000/login"
API_GET_URL = "http://127.0.0.1:8000/user/login/{username}"
API_POST_URL = "http://127.0.0.1:8000/token"

class UserLoginForm(StatesGroup):
    username = State()
    password = State()

@router.message(Command("login"))
async def wait_username(message: types.Message, state: FSMContext):
    await message.answer("Enter the username of your user:")
    await state.set_state(UserLoginForm.username)

@router.message(UserLoginForm.username)
async def check_username(message: types.Message, state: FSMContext):
    await state.update_data(telegram_id=message.from_user.id)
    async with httpx.AsyncClient() as client:
        response = await client.get(API_GET_URL.format(username=message.text))

    if response.status_code == 401:
        await message.answer("This username don't exists. Enter another:")
        return

    await message.answer("Enter the password:")
    await state.update_data(username=message.text, user_id=response.json().get("id"))
    await state.set_state(UserLoginForm.password)

@router.message(UserLoginForm.password)
async def check_password(message: types.Message, state: FSMContext):
    data = await state.get_data()
    username = data.pop("username")
    async with httpx.AsyncClient() as client:
        response = await client.post(API_URL, data={"username": username, "password": message.text})

    if response.status_code == 200:
        await state.update_data(access_token=response.json().get("access_token"))
        await message.answer("User login successfully")
        await add_token(message, state)
    else:
        await message.answer(f"Error:{response.text}")
        await state.clear()

async def add_token(message: types. Message, state: FSMContext):
    data = await state.get_data()
    async with httpx.AsyncClient() as client:
        response = await client.post(API_POST_URL, json=data)

    if response.status_code != 200:
        await message.answer(f"Error:{response.text}")

    await state.clear()