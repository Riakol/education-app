from aiogram.filters.state import State, StatesGroup

class StudentLevelGroup(StatesGroup):
    main_menu = State()
    choose_level = State()
    choose_group = State()
    select_group = State()
    inside_group = State()
    student_name = State()
    student_group_view = State()
    create_group = State()
    delete_group = State()

