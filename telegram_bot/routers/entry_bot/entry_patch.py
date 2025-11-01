from aiogram import Router, types
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
import httpx

router = Router()
API_URL = "http://127.0.0.1:8000/entries/{entry_id}"

class PatchEntryForm(StatesGroup):
    waiting_id = State()
    waiting_attribute = State()
    edit_attribute = State()
    waiting_confirm = State()

@router.message(Command("edit_entry"))
async def start_patch(message: types.Message, state: FSMContext):
    await message.answer("Enter the id of entry:")
    await state.set_state(PatchEntryForm.waiting_id)

@router.message(PatchEntryForm.waiting_id)
async def get_entry(message: types.Message, state: FSMContext):
    try:
        entry_id = int(message.text)
        if not entry_id.is_integer():
            raise ValueError
    except ValueError:
        await message.answer("Enter a integer number")
        return

    async with httpx.AsyncClient() as client:
        response = await client.get(API_URL.format(entry_id=entry_id))

    if response.status_code != 200:
        await message.answer("Entered a wrong id, try again ❌")
        return

    await state.update_data(entry_id=entry_id, updates={})
    await message.answer("What exactly you want update?\n"
                         "Title?\n"
                         "Description?\n"
                         "Tags?\n"
                         "Mood_score?\n"
                         "Progress_score?\n"
                         "Learning_hours?\n"
                         "Topic_id?")
    await state.set_state(PatchEntryForm.waiting_attribute)

@router.message(PatchEntryForm.waiting_attribute)
async def wait_attribute(message: types.Message, state: FSMContext):
    attributes = ["title", "description", "tags", "mood_score", "progress_score", "learning_hours", "topic_ids"]
    try:
        attribute = message.text.strip().lower()
        if not attribute in attributes:
            raise ValueError
    except ValueError:
        await message.answer("Enter a attribute that exists:")
        return

    await state.update_data(current_attribute=attribute)
    await message.answer("Enter a new value for attribute:")
    await state.set_state(PatchEntryForm.edit_attribute)

@router.message(PatchEntryForm.edit_attribute)
async def edit_attribute(message: types.Message, state: FSMContext):
    data = await state.get_data()
    attribute = data["current_attribute"]
    updates = data["updates"]
    value = message.text.strip()

    if attribute in ["mood_score", "progress_score"]:
        try:
            value = int(value)
            if not (0 <= value <= 10):
                raise ValueError
        except ValueError:
            await message.answer("Enter number between 0 and 10")
            return
    elif attribute == "learning_hours":
        try:
            value = float(value)
            if value < 0:
                raise ValueError
        except ValueError:
            await message.answer("Enter number more than 0")
            return
    elif attribute == "topic_ids":
        if not (value.startswith("[") and value.endswith("]")):
            await message.answer("Enter in this format: [1, 2, 3]")
            return

        items = value[1:-1].replace(" ", "").split(",")

        if not all(item.isdigit() for item in items):
            await message.answer("Enter only integers by comma: [1, 2, 3]")
            return

        value = list(map(int, items))

    updates[attribute] = value
    await state.update_data(updates=updates)

    await message.answer("Field added to changes\n"
                         "Would you update anything else?(yes/no)")
    await state.set_state(PatchEntryForm.waiting_confirm)

@router.message(PatchEntryForm.waiting_confirm)
async def confirm(message: types.Message, state: FSMContext):
    if message.text.strip().lower() in ["да", "yes"]:
        await message.answer("What exactly you want update?\n"
                             "Title?\n"
                             "Description?\n"
                             "Tags?\n"
                             "Mood score?\n"
                             "Progress score?\n"
                             "Learning hours?\n"
                             "Topic id?")
        await state.set_state(PatchEntryForm.waiting_attribute)
        return

    data = await state.get_data()
    entry_id = data["entry_id"]
    updates = data["updates"]

    async with httpx.AsyncClient() as client:
        response = await client.patch(API_URL.format(entry_id=entry_id), json=updates)

    if response.status_code == 200:
        await message.answer("Entry successfully updated ✅")
    else:
        await message.answer(f"Error:{response.text}")

    await state.clear()