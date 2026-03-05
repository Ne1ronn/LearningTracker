from aiogram.fsm.state import StatesGroup, State

class UpdateEntryForm(StatesGroup):
    waiting_id = State()
    title = State()
    description = State()
    tags = State()
    mood_score = State()
    progress_score = State()
    learning_hours = State()
    private = State()
    waiting_ids = State()
    topic_ids = State()

class PatchEntryForm(StatesGroup):
    waiting_id = State()
    waiting_attribute = State()
    edit_attribute = State()
    edit_topic_ids = State()
    waiting_confirm = State()

class DeleteEntryState(StatesGroup):
    waiting_id = State()

class EntryForm(StatesGroup):
    title = State()
    description = State()
    tags = State()
    mood_score = State()
    progress_score = State()
    learning_hours = State()
    private = State()
    waiting_ids = State()
    topic_ids = State()

class GetEntryState(StatesGroup):
    waiting_id = State()

class EntriesState(StatesGroup):
    waiting_private = State()
    waiting_date = State()
    waiting_mood = State()
    waiting_progress = State()
    waiting_hours = State()
    sort_date = State()
    sort_mood = State()
    sort_progress = State()
    sort_hours = State()
