from aiogram import types
from .topic_states import PatchTopicForm
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from .topic_router import router
import httpx

API_URL = "http://127.0.0.1:8000/topic/{topic_id}"
API_GET_URL = "http://127.0.0.1:8000/token/{telegram_id}"
API_TOKEN_URL = "http://127.0.0.1:8000/auth/validate"
API_ADMIN_URL = "http://127.0.0.1:8000/auth/validate/admin"

@router.message(Command("edit_topic"))
async def start_patch(message: types.Message, state: FSMContext):
    telegram_id = message.from_user.id
    async with httpx.AsyncClient() as client:
        response = await client.get(API_GET_URL.format(telegram_id=telegram_id))

    if response.status_code != 200:
        await message.answer(f"User with telegram id {telegram_id} unauthorized. Use command /login for authorize")
        await state.clear()
        return

    token = response.json().get("access_token")

    async with httpx.AsyncClient() as client:
        response = await client.get(API_TOKEN_URL, headers={"Authorization": f"Bearer {token}"})

    if response.status_code != 200:
        await message.answer(f"User didn't authorize. Use command /login for authorize")
        await state.clear()
        return

    async with httpx.AsyncClient() as client:
        response = await client.get(API_ADMIN_URL, headers={"Authorization": f"Bearer {token}"})

    if response.status_code != 200:
        await message.answer("You don't have enough permissions")
        await state.clear()
        return

    await state.update_data(token=token)

    await message.answer("Enter the id of topic:")
    await state.set_state(PatchTopicForm.waiting_id)

@router.message(PatchTopicForm.waiting_id)
async def get_topic(message: types.Message, state: FSMContext):
    try:
        topic_id = int(message.text)
        if not topic_id.is_integer():
            raise ValueError
    except ValueError:
        await message.answer("Enter a integer number")
        return

    async with httpx.AsyncClient() as client:
        response = await client.get(API_URL.format(topic_id=topic_id))

    if response.status_code != 200:
        await message.answer("Entered a wrong id, try again ❌")
        return

    await state.update_data(topic_id=topic_id, updates={})
    await message.answer("What exactly you want update?\n"
                         "Title?\n"
                         "Skill?\n"
                         "Need?\n"
                         "Progress_score?\n"
                         "Is active?")
    await state.set_state(PatchTopicForm.waiting_attribute)

@router.message(PatchTopicForm.waiting_attribute)
async def wait_attribute(message: types.Message, state: FSMContext):
    attributes = ["title", "skill", "need", "progress_score", "is_active"]
    try:
        attribute = message.text.strip().lower()
        if not attribute in attributes:
            raise ValueError
    except ValueError:
        await message.answer("Enter a attribute that exists:")
        return

    await state.update_data(current_attribute=attribute)
    await message.answer("Enter a new value for attribute:")
    await state.set_state(PatchTopicForm.edit_attribute)

@router.message(PatchTopicForm.edit_attribute)
async def patch_topic(message: types.Message, state: FSMContext):
    data = await state.get_data()
    attribute = data["current_attribute"]
    updates = data["updates"]
    value = message.text.strip()

    if attribute in ["need", "progress_score"]:
        try:
            value = int(value)
            if not (0 <= value <= 10):
                raise ValueError
        except ValueError:
            await message.answer("Enter number between 0 and 10")
            return

    updates[attribute] = value
    await state.update_data(updates=updates)

    await message.answer("Field added to changes\n"
                         "Would you update anything else?(yes/no)")
    await state.set_state(PatchTopicForm.waiting_confirm)

@router.message(PatchTopicForm.waiting_confirm)
async def confirm(message: types.Message, state: FSMContext):
    if message.text.strip().lower() in ["да", "yes"]:
        await message.answer("What exactly you want update?\n"
                             "Title?\n"
                             "Skill?\n"
                             "Need?\n"
                             "Progress_score?\n"
                             "Is active?")
        await state.set_state(PatchTopicForm.waiting_attribute)
        return

    data = await state.get_data()
    topic_id = data["topic_id"]
    updates = data["updates"]
    token = data.pop("token")

    async with httpx.AsyncClient() as client:
        response = await client.patch(API_URL.format(topic_id=topic_id), json=updates, headers={"Authorization": f"Bearer {token}"})

    if response.status_code == 200:
        await message.answer("Topic successfully updated ✅")
    else:
        await message.answer(f"Error:{response.text}")

    await state.clear()