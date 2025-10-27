from aiogram import Router, types
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
import httpx

router = Router()
API_URL = "http://127.0.0.1:8000/entries"

class EntryForm(StatesGroup):
    title = State()
    description = State()
    tags = State()
    mood_score = State()
    progress_score = State()
    learning_hours = State()
    waiting_ids = State()
    topic_ids = State()

@router.message(Command("add_entry"))
async def start_entry(message: types.Message, state: FSMContext):
    await message.answer("Enter the title of entry:")
    await state.set_state(EntryForm.title)

@router.message(EntryForm.title)
async def get_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Now the description:")
    await state.set_state(EntryForm.description)

@router.message(EntryForm.description)
async def get_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Now the tags(separated by commas):")
    await state.set_state(EntryForm.tags)

@router.message(EntryForm.tags)
async def get_tags(message: types.Message, state: FSMContext):
    await state.update_data(tags=message.text)
    await message.answer("Now the mood score:")
    await state.set_state(EntryForm.mood_score)

@router.message(EntryForm.mood_score)
async def get_mood(message: types.Message, state: FSMContext):
    try:
        score = int(message.text)
        if not (0 <= score <= 10):
            raise ValueError
    except ValueError:
        await message.answer("Enter number between 0 and 10")
        return
    await state.update_data(mood_score=score)
    await message.answer("Now the progress score:")
    await state.set_state(EntryForm.progress_score)

@router.message(EntryForm.progress_score)
async def get_progress(message: types.Message, state: FSMContext):
    try:
        score = int(message.text)
        if not (0 <= score <= 10):
            raise ValueError
    except ValueError:
        await message.answer("Enter number between 0 and 10")
        return

    await state.update_data(progress_score=score)
    await message.answer("Now the learning hours:")
    await state.set_state(EntryForm.learning_hours)

@router.message(EntryForm.learning_hours)
async def get_hours(message: types.Message, state: FSMContext):
    try:
        hours = float(message.text)
        if hours < 0:
            raise ValueError
    except ValueError:
        await message.answer("Enter number more than 0")
        return

    await state.update_data(learning_hours=hours)
    await message.answer("Do you want add id of related topics?")
    await state.set_state(EntryForm.waiting_ids)

@router.message(EntryForm.waiting_ids)
async def waiting_ids(message: types.Message, state: FSMContext):
    if message.text.lower() == "yes":
        await message.answer("Enter the id's by square brackets: [1, 2]")
        await state.set_state(EntryForm.topic_ids)
    else:
        await add_entry(message, state)


@router.message(EntryForm.topic_ids)
async def add_topics(message: types.Message, state: FSMContext):
    text = message.text.strip()

    if not (text.startswith("[") and text.endswith("]")):
        await message.answer("Enter in this format: [1, 2, 3]")
        return

    items = text[1:-1].replace(" ", "").split(",")

    if not all(item.isdigit() for item in items):
        await message.answer("Enter only integers by comma: [1, 2, 3]")
        return

    topic_ids = list(map(int, items))
    await state.update_data(topic_ids=topic_ids)
    await add_entry(message, state)


async def add_entry(message: types.Message, state: FSMContext):
    data = await state.get_data()

    async with httpx.AsyncClient() as client:
        response = await client.post(API_URL, json=data)

    if response.status_code == 200:
        await message.answer("Entry added to database ✅")
    else:
        await message.answer(f"Error:{response.text}")

    await state.clear()