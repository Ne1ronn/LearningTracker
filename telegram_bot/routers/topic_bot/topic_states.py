from aiogram.fsm.state import StatesGroup, State

class TopicForm(StatesGroup):
    title = State()
    skill = State()
    need = State()
    progress_score = State()
    is_active = State()

class DeleteTopicState(StatesGroup):
    waiting_id = State()

class GetTopicState(StatesGroup):
    waiting_id = State()

class PatchTopicForm(StatesGroup):
    waiting_id = State()
    waiting_attribute = State()
    edit_attribute = State()
    waiting_confirm = State()

class UpdateTopicForm(StatesGroup):
    waiting_id = State()
    title = State()
    skill = State()
    need = State()
    progress_score = State()
    is_active = State()