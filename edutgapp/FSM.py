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
    mark_group_attendance = State()
    absence_student_selected = State()
    input_absence_reason = State()

class Attendance(StatesGroup):
    attendance = State()
    get_custom_excel = State()
    attendance_start_year = State()
    attendance_start_month = State()
    attendance_start_day = State()
    attendance_end_year = State()
    attendance_end_month = State()
    attendance_end_day = State()

class Student(StatesGroup):
    editing_student_menu = State() 
    remove_student = State()
    rename_student = State()
    update_student_name = State()
    transfer_student = State()
    transfer_student_level = State()
    transfer_student_group = State()

