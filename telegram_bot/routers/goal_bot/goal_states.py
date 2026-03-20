from aiogram.fsm.state import StatesGroup, State


class GoalAddState(StatesGroup):
    waiting_topic_id = State()
    waiting_target_hours = State()
    waiting_target_date = State()


class GoalGetState(StatesGroup):
    waiting_id = State()


class GoalDeleteState(GoalGetState):
    waiting_id = State()


class GoalStatsState(StatesGroup):
    waiting_id = State()


class GoalPatchState(StatesGroup):
    waiting_id = State()
    waiting_attribute = State()
    edit_attribute = State()
    waiting_confirm = State()
