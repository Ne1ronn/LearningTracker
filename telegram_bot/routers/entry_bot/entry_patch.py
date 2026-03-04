from aiogram import types, F
from .entry_states import PatchEntryForm
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from ...keyboards import create_entry_attribute_choose_buttons, create_yes_no_buttons, create_cancel_button
from .entry_router import router
import httpx

API_URL = "http://127.0.0.1:8000/entries/{entry_id}"
API_PERMISSION_URL = "http://127.0.0.1:8000/entries/{entry_id}/edit"

@router.callback_query(F.data == "patch_entry")
async def start_patch(cb: CallbackQuery, state: FSMContext, token: str):
    await state.clear()
    await cb.answer()

    await state.update_data(token=token)
    await cb.message.answer("Enter the id of entry:", reply_markup=create_cancel_button())
    await state.set_state(PatchEntryForm.waiting_id)

@router.message(PatchEntryForm.waiting_id)
async def get_entry(message: types.Message, state: FSMContext):
    try:
        entry_id = int(message.text)
    except ValueError:
        await message.answer("Enter a integer number", reply_markup=create_cancel_button())
        return

    data = await state.get_data()
    token = data.pop("token")

    async with httpx.AsyncClient() as client:
        response = await client.get(API_PERMISSION_URL.format(entry_id=entry_id), headers={"Authorization": f"Bearer {token}"})

    if response.status_code in (403, 404):
        await message.answer(response.text)
        await state.clear()
        return

    await state.update_data(entry_id=entry_id, updates={})
    await message.answer("What exactly you want update?", reply_markup=create_entry_attribute_choose_buttons())
    await state.set_state(PatchEntryForm.waiting_attribute)

@router.callback_query(PatchEntryForm.waiting_attribute)
async def wait_attribute(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    attribute = cb.data

    if cb.data == "cancel":
        await state.clear()
        await cb.message.answer("Operation cancelled")
        return

    attributes = [
        "title",
        "description",
        "tags",
        "mood_score",
        "progress_score",
        "learning_hours",
        "private",
        "topic_ids",
    ]

    if attribute not in attributes:
        await cb.answer("Invalid attribute", show_alert=True)
        return

    await state.update_data(current_attribute=attribute)
    await cb.message.answer("Enter a new value for attribute:", reply_markup=create_cancel_button())
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
            await message.answer("Enter number between 0 and 10", reply_markup=create_cancel_button())
            return
    elif attribute == "learning_hours":
        try:
            value = float(value)
            if value < 0 or value > 24:
                raise ValueError
        except ValueError:
            await message.answer("Enter number more than 0 and less than 24", reply_markup=create_cancel_button())
            return
    elif attribute == "topic_ids":
        if not (value.startswith("[") and value.endswith("]")):
            await message.answer("Enter in this format: [1, 2, 3]", reply_markup=create_cancel_button())
            return

        items = value[1:-1].replace(" ", "").split(",")

        if not all(item.isdigit() for item in items):
            await message.answer("Enter only integers by comma: [1, 2, 3]", reply_markup=create_cancel_button())
            return

        value = list(map(int, items))

    updates[attribute] = value
    await state.update_data(updates=updates)

    await message.answer("Field added to changes\n"
                         "Would you update anything else?",
                         reply_markup=create_yes_no_buttons("field"))
    await state.set_state(PatchEntryForm.waiting_confirm)

@router.callback_query(PatchEntryForm.waiting_confirm)
async def confirm(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    if cb.data == "yes_field":
        await cb.message.answer("What exactly you want update?", reply_markup=create_entry_attribute_choose_buttons())
        await state.set_state(PatchEntryForm.waiting_attribute)
        return

    data = await state.get_data()
    entry_id = data["entry_id"]
    updates = data["updates"]
    token = data.pop("token")

    async with httpx.AsyncClient() as client:
        response = await client.patch(API_URL.format(entry_id=entry_id), json=updates, headers={"Authorization": f"Bearer {token}"})

    if response.status_code == 200:
        await cb.message.answer("Entry successfully updated ✅")
    else:
        await cb.message.answer(f"Error:{response.text}")
        await state.clear()
        return

    await state.clear()