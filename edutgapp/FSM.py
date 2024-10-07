from aiogram.filters.state import State, StatesGroup



class StudentWorkflow(StatesGroup):
    choose_level = State()

    student_name = State()
    remove_student = State()

    choose_group = State()
    select_group = State()
    inside_group = State()
    student_group_view = State()
    create_group = State()
    delete_group = State()

    attendance = State()
    attendance_by_msg = State()
    attendance_year = State()
    attendance_month = State()


# class Level(StatesGroup):
#     choose_level = State()
