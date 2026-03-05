from aiogram import types, F
from .entry_states import PatchEntryForm
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from ...keyboards import create_entry_attribute_choose_buttons, create_yes_no_buttons, create_cancel_button, \
    create_topics_buttons
from .entry_router import router
import httpx

API_URL = "http://127.0.0.1:8000/entries/{entry_id}"
API_PERMISSION_URL = "http://127.0.0.1:8000/entries/{entry_id}/edit"
API_TOPICS_URL = "http://127.0.0.1:8000/topics"

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

    topic_ids = []
    if response.status_code == 200:
        topic_ids = [t["id"] for t in response.json()["topics"]]

    await state.update_data(entry_id=entry_id, topic_ids=topic_ids, updates={})
    await message.answer("What exactly you want update?", reply_markup=create_entry_attribute_choose_buttons())
    await state.set_state(PatchEntryForm.waiting_attribute)

@router.callback_query(PatchEntryForm.waiting_attribute)
async def wait_attribute(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    attribute = cb.data
    data = await state.get_data()
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

    if attribute == "topic_ids":
        async with httpx.AsyncClient() as client:
            response = await client.get(API_TOPICS_URL)

        if response.status_code == 200:
            topics = response.json()
        else:
            await cb.message.answer(f"Received error: {response.text}")
            await state.set_state(PatchEntryForm.waiting_confirm)
            return

        topic_map = {int(t["id"]): t["title"] for t in topics}
        topics_ids = data["topic_ids"]
        if not topics_ids:
            await cb.message.answer("Existed topics of entry: none")
        else:
            titles = [topic_map.get(i, str(i)) for i in topics_ids]
            text = "Existed topics of entry:\n" + "\n".join(f"• {t}" for t in titles)
            await cb.message.answer(text)
        await cb.message.answer("Add or clear topics:", reply_markup=create_topics_buttons(topics))
        await state.update_data(topics=topics, topic_map=topic_map)
        await state.set_state(PatchEntryForm.edit_topic_ids)
        return

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

    updates[attribute] = value
    await state.update_data(updates=updates)

    await message.answer("Field added to changes\n"
                         "Would you update anything else?",
                         reply_markup=create_yes_no_buttons("field"))
    await state.set_state(PatchEntryForm.waiting_confirm)


@router.callback_query(PatchEntryForm.edit_topic_ids)
async def add_topics(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    data = await state.get_data()
    topics = data["topics"]
    if cb.data == "cancel":
        await state.clear()
        await cb.message.answer("Operation cancelled")
        return

    elif cb.data == "clear":
        await state.update_data(topic_ids=[])
        await cb.message.answer("Topics cleared", reply_markup=create_topics_buttons(topics))
        return

    elif cb.data == "ready":
        await cb.message.answer("Field added to changes\n"
                             "Would you update anything else?",
                             reply_markup=create_yes_no_buttons("field"))
        updates = data["updates"]
        updates["topic_ids"] = data["topic_ids"]
        await state.update_data(updates=updates)
        await state.set_state(PatchEntryForm.waiting_confirm)
        return

    elif cb.data.startswith("topic_"):
        topic_id = int(cb.data.split("_")[1])
        topics_ids = data["topic_ids"]

        if topic_id in topics_ids:
            await cb.message.answer(f"Topic {topic_id} already in list")
            return

        topics_ids.append(topic_id)

        topic_map = data["topic_map"]
        titles = [topic_map.get(i, str(i)) for i in topics_ids]
        text = "Selected topics:\n" + "\n".join(f"• {t}" for t in titles)

        await state.update_data(topic_ids=topics_ids)
        await cb.message.answer(text, reply_markup=create_topics_buttons(topics))
        return
    else:
        await cb.message.answer("Wrong button. Please choose right one")
        return

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