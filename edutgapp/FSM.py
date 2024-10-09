from aiogram.filters.state import State, StatesGroup

class Level(StatesGroup):
    choose_level = State()

class Group(StatesGroup):
    choose_group = State()
    select_group = State()
    inside_group = State()
    student_group_view = State()
    create_group = State()
    delete_group = State()
    input_student_name = State()

class Attendance(StatesGroup):
    attendance = State()
    attendance_by_msg = State()
    attendance_year = State()
    attendance_month = State()

class Student(StatesGroup):
    editing_student_menu = State() 
    remove_student = State()
    rename_student = State()
    update_student_name = State()

