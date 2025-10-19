from aiogram import Router, types
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from models.entry_model import EntryModel

router = Router()

class AddEntry(StatesGroup):
    waiting_for_field = State()

FIELDS = ["title", "description", "mood"]

@router.message(Command("Add_entry"))
async def start_add_entry(message: types.Message, state: FSMContext):
    await state.update_data(current_index=0, data={})
    await message.answer(f"Введите {FIELDS[0]}:")
    await state.set_state(AddEntry.waiting_for_field)

@router.message(AddEntry.waiting_for_field)
async def process_field(message: types.Message, state: FSMContext):
    data = await state.get_data()
    current_index = data["current_index"]
    entry_data = data.get("data", {})

    field_name = FIELDS[current_index]
    entry_data[field_name] = message.text

    current_index += 1

    if current_index < len(FIELDS):
        await state.update_data(current_index=current_index, data=entry_data)
        await message.answer(f"Введите {FIELDS[current_index]}:")
    else:
        await message.answer("✅ Запись создана:\n" + "\n".join(f"{k}: {v}" for k, v in entry_data.items()))
        await state.clear()
