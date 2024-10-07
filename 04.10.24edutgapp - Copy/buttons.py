from datetime import datetime
from aiogram.types import Message, CallbackQuery
from aiogram_dialog.widgets.kbd import Button, Back, Group
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog import (
    Dialog, DialogManager, setup_dialogs, StartMode, Window, ChatEvent, 
)
from aiogram_dialog.widgets.kbd import Checkbox, ManagedCheckbox
from database import engine, requests
from FiniteStateMachine import StudentLevelGroup
from typing import Any
from attendance_data import create_attendance_excel
from main import bot
from aiogram.types import InputFile


async def check_changed(event: ChatEvent, checkbox: ManagedCheckbox,
                        manager: DialogManager):
    print("Check status changed:", checkbox.is_checked())
  


async def check_saved(event: ChatEvent, checkbox: ManagedCheckbox,
                        manager: DialogManager):
    
    current_date = datetime.now().date()
    eng_lvl_id = await requests.get_lvl_id(manager.dialog_data.get('selected_level'))
    group_id = await requests.get_group_number(int(manager.dialog_data.get('group_selected')))
    
    group_details_id = await requests.get_group_details_id(eng_lvl_id, group_id)
    all_students_group = await requests.get_students_from_group(group_details_id)

    widget = manager.dialog().find("student_check").get_checked(manager)

    if widget:
        for student_name_present in widget:
            if student_name_present in all_students_group:
                student_id = await requests.get_student_id(student_name_present)
                student_details_id = await requests.get_student_details_id(student_id, group_details_id)

                status = "present"
                await requests.add_student_attendance(student_details_id, current_date, status)

        for student_name_absent in all_students_group:
            if student_name_absent not in widget:
                student_id = await requests.get_student_id(student_name_absent)
                student_details_id = await requests.get_student_details_id(student_id, group_details_id)
                await requests.add_student_attendance(student_details_id, current_date)
    else:
        for student_name in all_students_group:
            student_id = await requests.get_student_id(student_name)
            student_details_id = await requests.get_student_details_id(student_id, group_details_id)
            await requests.add_student_attendance(student_details_id, current_date)
    
    await event.answer("✅ The data has been saved successfully!")
    
    await manager.switch_to(StudentLevelGroup.inside_group)


async def level_button_clicked(callback: CallbackQuery, button: Button, manager: DialogManager):
    selected_level = button.widget_id
    manager.dialog_data['selected_level'] = requests.levels[selected_level]
    
    await manager.next()


async def create_level_buttons():

    eng_levels = [
        Button(
            Const(x),
            id=f"{x.lower().replace('-', '')}",
            on_click=level_button_clicked,
        ) for x in await engine.student_levels()
    ]

    return eng_levels


async def create_group_clicked(callback: CallbackQuery, button: Button, manager: DialogManager):
    await manager.switch_to(StudentLevelGroup.create_group)


async def create_group(callback: CallbackQuery, button: Button, manager: DialogManager):
    """ Обработка создания новой группы """
    selected_level = manager.dialog_data.get('selected_level')

    conn = await engine.connect_to_db()

    try:
        group_number = await requests.find_or_create_group(conn, selected_level)
        await callback.answer(f"Группа {group_number} для уровня {selected_level} была создана.")
    finally:
        await engine.close_db_connection(conn)

    await manager.switch_to(StudentLevelGroup.choose_group)


async def delete_group_clicked(callback: CallbackQuery, button: Button, manager: DialogManager):
    await manager.switch_to(StudentLevelGroup.delete_group)


async def delete_group(callback: CallbackQuery, button: Button, manager: DialogManager):
    
    conn = await engine.connect_to_db()
    eng_lvl_id = await requests.get_lvl_id(manager.dialog_data.get('selected_level'))
    group_id = await requests.get_group_number(int(manager.dialog_data.get('group_selected')))
    group_details_id = await requests.get_group_details_id(eng_lvl_id, group_id)

    get_students = await conn.fetch("""
            SELECT s.id 
            FROM student s
            JOIN student_details sd ON s.id = sd.student_id
            WHERE sd.group_details_id = $1;
        """, group_details_id)
        
    students_id = [record['id'] for record in get_students]

    await conn.fetchval("""
        DELETE FROM group_details WHERE id = $1
    """, group_details_id)

    if students_id:
        await conn.fetchval("""
            DELETE FROM student WHERE id = ANY($1::int[])
        """, students_id)

    
    await callback.answer(f"✅ the group was successfully deleted!")
 
    await manager.switch_to(StudentLevelGroup.choose_group)


async def get_group_buttons(selected_level):
    groups = await requests.get_groups_for_level(selected_level)

    if groups:
        group_buttons = [
            Button(Const(f"Group: {group_id['id']}"), id=f"{group_id['group_number']}", on_click=group_selected)
            for group_id in groups
        ]
    else:
        group_buttons = [] 

    return group_buttons 


async def get_groups_clicked(callback: CallbackQuery, button: Button, manager: DialogManager):
    """Обработчик для кнопки 'Select a group'."""
    
    selected_level = await requests.get_lvl_id(manager.dialog_data.get('selected_level'))
    user_id = callback.from_user.id
    print(user_id)

    await requests.insert_lvl_teacher_current_pos(selected_level, await requests.get_teacher_id(user_id))
    group_buttons = await get_group_buttons(selected_level)

    await manager.update({"group_buttons": group_buttons})
   
    await manager.switch_to(StudentLevelGroup.select_group)


async def group_selected(callback: CallbackQuery, button: Button, manager: DialogManager, item_id: str):
    """ Действие при выборе группы """
    await manager.update({"group_selected": item_id})
    
    # await callback.answer(f"You selected {item_id}!")
    await manager.next()


async def add_student_to_group(callback: CallbackQuery, button: Button, manager: DialogManager):
    print("Button 'Add a student' clicked")  # Проверка вызова функции
    await manager.switch_to(StudentLevelGroup.student_name)


async def remove_student_from_group(callback: CallbackQuery, button: Button, manager: DialogManager):
    print("Button 'Add a student' clicked")  # Проверка вызова функции
    # await manager.switch_to(StudentLevelGroup.student_name)
 

async def add_student(callback: CallbackQuery, button: Button, manager: DialogManager):
    conn = await engine.connect_to_db()

    student_name = manager.find("student_name").get_value()
    if student_name:
        print(f"Student name entered: {student_name}")

        await requests.add_student(student_name)
        student_id = await requests.get_student_id(student_name)
        eng_lvl_id = await requests.get_lvl_id(manager.dialog_data.get('selected_level'))
        group_id = await requests.get_group_number(int(manager.dialog_data.get('group_selected')))

        await requests.add_student_to_group(student_id, await requests.get_group_details_id(eng_lvl_id, group_id))


    else:
        print("No student name entered.")
    
    await manager.next()
    

async def show_students(callback: CallbackQuery, button: Button, manager: DialogManager):
    eng_lvl_id = await requests.get_lvl_id(manager.dialog_data.get('selected_level'))
    group_id = await requests.get_group_number(int(manager.dialog_data.get('group_selected')))

    students = await requests.get_students_from_group(await requests.get_group_details_id(eng_lvl_id, group_id))
    print(f"Button 'View all students' clicked: {students}")

    await manager.update({"show_group_students": students})
    await manager.switch_to(StudentLevelGroup.student_group_view)



async def show_attendance(callback: CallbackQuery, button: Button, manager: DialogManager):
    
    eng_lvl_id = await requests.get_lvl_id(manager.dialog_data.get('selected_level'))
    group_id = await requests.get_group_number(int(manager.dialog_data.get('group_selected')))
    gdi = await requests.get_group_details_id(eng_lvl_id, group_id)

    month_name = 10
    year = 2024

    data = await requests.attendance_data(gdi, month_name, year)
   
    message = create_attendance_excel(data, month_name, year)
   
    await callback.message.answer(message)
    # with open(file_name, 'rb') as file:
    # await callback.message.answer_document(input_file)

    # await callback.message.answer("Файл с посещаемостью отправлен.")






async def dialog_get_data(dialog_manager: DialogManager, **kwargs):
    context = dialog_manager.current_context()
    data = context.dialog_data
   
    return {
        "group_buttons": data.get("group_buttons", []), 
        "name": "Obayash", 
        "selected_level": data.get("selected_level"),
        "group_selected": data.get("group_selected"),     
        "students_view": data.get("show_group_students"),     
    }


