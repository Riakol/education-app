from aiogram.filters.state import State, StatesGroup

class StudentLevelGroup(StatesGroup):
    choose_level = State()
    choose_group = State()
    select_group = State()