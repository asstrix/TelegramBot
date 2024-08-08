from aiogram.fsm.state import State, StatesGroup


class EventState(StatesGroup):
    edit_event = State()
    delete_event = State()
    join_account = State()
    title = State()
    description = State()
    spec_end_time = State()
    start_time = State()
    end_time = State()
    year = State()
    month = State()
    day = State()

