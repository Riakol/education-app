import FSM
import ast

from datetime import datetime
from aiogram.types import CallbackQuery
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const
from aiogram_dialog import (
    DialogManager, ChatEvent, StartMode
)
from aiogram_dialog.widgets.kbd import ManagedCheckbox
from database import engine, requests
from typing import Any



async def level_menu(callback: CallbackQuery, button: Button, manager: DialogManager):
    await manager.done()

async def check_saved(event: ChatEvent, checkbox: ManagedCheckbox,
                        manager: DialogManager):
        
    current_date = datetime.now().date()
    eng_lvl_id = await requests.get_lvl_id(manager.start_data['selected_level'])
    group_id = await requests.get_group_number(int(manager.dialog_data.get('group_selected')))
    
    group_details_id = await requests.get_group_details_id(eng_lvl_id, group_id)
    
    student_names = await requests.get_students_from_group(group_details_id)
    all_students_group = [(name, id) for name, id in student_names]

    student_dict = {id: name for name, id in all_students_group}

    widget = manager.dialog().find("student_check").get_checked(manager)

    if widget:
        widget_tuples = [ast.literal_eval(student) for student in widget]

        for student_tuple in widget_tuples:
            student_name_present, student_id_present = student_tuple
            if student_id_present in student_dict:
                student_details_id = await requests.get_student_details_id(student_id_present, group_details_id)
                print(student_details_id)

                status = "present"
                await requests.add_student_attendance(student_details_id, current_date, status)

        for student_name_absent, student_id in all_students_group:
            if student_id not in [id for _, id in widget_tuples]:
                student_details_id = await requests.get_student_details_id(student_id, group_details_id)
                await requests.add_student_attendance(student_details_id, current_date)
    else:
        for student_name, student_id in all_students_group:
            student_details_id = await requests.get_student_details_id(student_id, group_details_id)
            await requests.add_student_attendance(student_details_id, current_date)
    
    await event.answer("✅ The data has been saved successfully!")
    
    await manager.switch_to(FSM.Group.inside_group)


async def other_check_saved(event: ChatEvent, checkbox: ManagedCheckbox,
                        manager: DialogManager):
        
    widget = manager.dialog().find("student_check").get_checked(manager)
    await manager.update({"other_check_saved": widget})

    # await event.answer("✅ The data has been saved successfully!")
    
    await manager.switch_to(FSM.Group.input_absence_reason)


async def create_group(callback: CallbackQuery, button: Button, manager: DialogManager):
    """ Обработка создания новой группы """
    selected_level = manager.start_data['selected_level']

    conn = await engine.connect_to_db()

    try:
        group_number = await requests.find_or_create_group(conn, selected_level)
        await callback.answer(f"Группа {group_number} для уровня {selected_level} была создана.")
    finally:
        await engine.close_db_connection(conn)

    await manager.switch_to(FSM.Group.choose_group)


async def delete_group(callback: CallbackQuery, button: Button, manager: DialogManager):
    
    conn = await engine.connect_to_db()
    eng_lvl_id = await requests.get_lvl_id(manager.start_data['selected_level'])
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
 
    await manager.switch_to(FSM.Group.choose_group)


async def get_group_buttons(selected_level):
    groups = await requests.get_groups_for_level(selected_level)

    if groups:
        group_buttons = [
            (group_id['group_number'], Button(text=Const(f"Group: {group_id['group_number']}"), id=f"{group_id['id']}", on_click=group_selected))
            for group_id in groups
            # (group_id['group_number'], Button(text=Const(f"Group: {group_id['id']}"), id=f"{group_id['group_number']}", on_click=group_selected))
            # for group_id in groups
        ]
    else:
        group_buttons = [] 

    return group_buttons


async def get_groups_clicked(callback: CallbackQuery, button: Button, manager: DialogManager):
    """Обработчик для кнопки 'Select a group'."""
    
    selected_level = await requests.get_lvl_id(manager.start_data["selected_level"])
    group_buttons = await get_group_buttons(selected_level)

    await manager.update({"selected_level": selected_level})
    await manager.update({"group_buttons": group_buttons})
   
    await manager.switch_to(FSM.Group.select_group)


async def group_selected(callback: CallbackQuery, button: Button, manager: DialogManager, item_id: str):
    await manager.update({"group_selected": item_id})
    #item_id это id группы, а не имя группы
    
    await manager.next()


async def editing_student(callback: CallbackQuery, button: Button, manager: DialogManager):
    eng_lvl_id = await requests.get_lvl_id(manager.start_data['selected_level'])
    group_id = await requests.get_group_number(int(manager.dialog_data.get('group_selected')))
    
    group_details_id = await requests.get_group_details_id(eng_lvl_id, group_id)
    
    students = await requests.get_students_from_group(group_details_id)

    if students:
        student_buttons = [
            (name, Button(Const(f"{name}"), id=f"id_{student_id}"))
            for name, student_id in students
        ]
        student_buttons = sorted(student_buttons, key=lambda x: x[0])
    else:
        student_buttons = []

    
    await manager.start(FSM.Student.editing_student_menu, data={"selected_level": manager.start_data['selected_level'],
                                                         "group_selected": manager.dialog_data.get('group_selected'),
                                                         "student_buttons": student_buttons})

async def student_absence_selected(callback: CallbackQuery, button: Button, manager: DialogManager, item_id: str):
    print(f"This is student_absence_selected {int(item_id.split('_')[1])}") # здесь будет id_42 например
    await manager.update({"studentid_absence_selected": int(item_id.split('_')[1])})
    await manager.switch_to(FSM.Group.input_absence_reason)


async def add_student(callback: CallbackQuery, button: Button, manager: DialogManager):

    student_name = manager.find("student_name").get_value()
    group_details_id = await requests.get_group_details_id(
        await requests.get_lvl_id(manager.start_data['selected_level']),
        await requests.get_group_number(int(manager.dialog_data.get('group_selected')))
    )

    if student_name:
        existing_students = await requests.get_students_from_group(group_details_id)

        if any(existing_student[0].lower() == student_name.lower() for existing_student in existing_students):
            await callback.answer(f"A student named '{student_name}' already exists in the group. Please choose a different name.")
            return

        student_id = await requests.add_student(student_name)

        await requests.add_student_to_group(student_id, group_details_id)
        await callback.answer(f"✅ The student '{student_name}' has been successfully added to the group.")

    
async def show_students(callback: CallbackQuery, button: Button, manager: DialogManager):
    eng_lvl_id = await requests.get_lvl_id(manager.start_data['selected_level'])
    group_id = await requests.get_group_number(int(manager.dialog_data.get('group_selected')))
    
    students = await requests.get_students_from_group(await requests.get_group_details_id(eng_lvl_id, group_id))
    student_names = [(name, id) for name, id in students]
 

    await manager.update({"show_group_students": student_names})
    await manager.switch_to(FSM.Group.student_group_view)


async def show_attendance(callback: CallbackQuery, button: Button, manager: DialogManager):
    await manager.start(FSM.Attendance.attendance, data={"selected_level": manager.start_data['selected_level'],
                                                         "group_selected": manager.dialog_data.get('group_selected')})
    
async def absence_reason(callback: CallbackQuery, button: Button, manager: DialogManager):
    current_date = datetime.now().date()

    absence = manager.find("absence_reason").get_value()
    print(absence)
    group_details_id = await requests.get_group_details_id(
        await requests.get_lvl_id(manager.start_data['selected_level']),
        await requests.get_group_number(int(manager.dialog_data.get('group_selected')))
    )
    student_details_id = await requests.get_student_details_id(manager.dialog_data.get('studentid_absence_selected'), group_details_id)

    await requests.add_student_absence_reason(student_details_id, current_date, absence)
    await callback.answer("✅ The data has been saved successfully!")


async def absence_student_btns(callback: CallbackQuery, button: Button, manager: DialogManager):
    eng_lvl_id = await requests.get_lvl_id(manager.start_data['selected_level'])
    group_id = await requests.get_group_number(int(manager.dialog_data.get('group_selected')))
    
    group_details_id = await requests.get_group_details_id(eng_lvl_id, group_id)
    
    students = await requests.get_students_from_group(group_details_id)

    if students:
        student_buttons = [
            (name, Button(Const(f"{name}"), id=f"id_{student_id}"))
            for name, student_id in students
        ]
        student_buttons = sorted(student_buttons, key=lambda x: x[0])
    else:
        student_buttons = []
    
    await manager.update({"student_buttons": student_buttons})
    await manager.switch_to(FSM.Group.absence_student_selected)