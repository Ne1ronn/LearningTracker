from email.charset import add_alias

from aiogram import Router, types
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
import httpx

router = Router()
API_URL = "http://127.0.0.1:8000/topics"

class TopicForm(StatesGroup):
    title = State()
    skill = State()
    need = State()
    progress_score = State()
    is_active = State()

@router.message(Command("add_topic"))
async def start_topic(message: types.Message, state: FSMContext):
    await message.answer("Enter the title of new topic:")
    await state.set_state(TopicForm.title)

@router.message(TopicForm.title)
async def add_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Now the skill of topic:")
    await state.set_state(TopicForm.skill)

@router.message(TopicForm.skill)
async def add_skill(message: types.Message, state: FSMContext):
    await state.update_data(skill=message.text)
    await message.answer("Now the need of topic:")
    await state.set_state(TopicForm.need)

@router.message(TopicForm.need)
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
    await state.set_state(TopicForm.progress_score)

@router.message(TopicForm.progress_score)
async def add_score(message: types.Message, state: FSMContext):
    try:
        score = int(message.text)
        if not (0 <= score <= 10):
            raise ValueError
    except ValueError:
        await message.answer("Enter number between 0 and 10")
        return

    await state.update_data(progress_score=score)