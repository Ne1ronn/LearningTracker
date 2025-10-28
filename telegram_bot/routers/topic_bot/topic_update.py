from aiogram import Router, types
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
import httpx

router = Router()
API_URL = "http://127.0.0.1:8000/topic/{topic_id}"

class UpdateTopicForm(StatesGroup):
    waiting_id = State()
    title = State()
    skill = State()
    need = State()
    progress_score = State()
    is_active = State()

@router.message(Command("update_topic"))
async def start_update(message: types.Message, state: FSMContext):
    await message.answer("Enter the id of topic:")
    await state.set_state(UpdateTopicForm.waiting_id)

@router.message(UpdateTopicForm.waiting_id)
async def update_topic(message: types.Message, state: FSMContext):
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

    await state.update_data(topic_id=topic_id)
    await message.answer("Enter the title of updated topic:")
    await state.set_state(UpdateTopicForm.title)

@router.message(UpdateTopicForm.title)
async def add_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Now the skill of topic:")
    await state.set_state(UpdateTopicForm.skill)

@router.message(UpdateTopicForm.skill)
async def add_skill(message: types.Message, state: FSMContext):
    await state.update_data(skill=message.text)
    await message.answer("Now the need of topic:")
    await state.set_state(UpdateTopicForm.need)

@router.message(UpdateTopicForm.need)
async def add_need(message: types.Message, state: FSMContext):
    try:
        score = int(message.text)
        if not (0 <= score <= 10):
            raise ValueError
    except ValueError:
        await message.answer("Enter number between 0 and 10")
        return
    await state.update_data(need=score)
    await message.answer("Now the progress score of topic:")
    await state.set_state(UpdateTopicForm.progress_score)

@router.message(UpdateTopicForm.progress_score)
async def add_score(message: types.Message, state: FSMContext):
    try:
        score = int(message.text)
        if not (0 <= score <= 10):
            raise ValueError
    except ValueError:
        await message.answer("Enter number between 0 and 10")
        return

    await state.update_data(progress_score=score)

    data = await state.get_data()
    topic_id = data.pop('topic_id')

    async with httpx.AsyncClient() as client:
        response = await client.put(API_URL.format(topic_id=topic_id), json=data)

    if response.status_code == 200:
        await message.answer("Topic successfully updated ✅")
    else:
        await message.answer(f"Error:{response.text}")