import FSM
import ast

from database.engine import db
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
    group_id = manager.dialog_data.get('group_selected_id')
    
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
    

    reminder = await get_reminder(all_students_group, group_details_id)
    if reminder:
        await event.message.answer(f"‼️ Today is the 12th lesson:\n\n{reminder}")

    await event.answer("✅ The data has been saved successfully!")
    await manager.switch_to(FSM.Group.inside_group)


async def other_check_saved(event: ChatEvent, checkbox: ManagedCheckbox,
                        manager: DialogManager):
        
    widget = manager.dialog().find("student_check").get_checked(manager)
    await manager.update({"other_check_saved": widget})
 
    await manager.switch_to(FSM.Group.input_absence_reason)


async def create_group(callback: CallbackQuery, button: Button, manager: DialogManager, item_id: str):
    """ Обработка создания новой группы """
    selected_level = manager.start_data['selected_level']
    group_name = item_id
    create_group_reqeust = await requests.create_group(selected_level, group_name)
    await callback.answer(create_group_reqeust)

    # selected_level = manager.start_data['selected_level']

    # conn = await engine.connect_to_db()

    # try:
    #     group_number = await requests.find_or_create_group(conn, selected_level)
    #     await callback.answer(f"Группа {group_number} для уровня {selected_level} была создана.")
    # finally:
    #     await engine.close_db_connection(conn)

    await manager.switch_to(FSM.Group.choose_group)


async def rename_group(callback: CallbackQuery, button: Button, manager: DialogManager, item_id: str):
    """ Обработка создания новой группы """
    selected_level = manager.start_data['selected_level']
    group_name = item_id
    gdi = await requests.get_group_details_id(await requests.get_lvl_id(selected_level), manager.dialog_data.get('group_selected_id'))

    rename_group_reqeust = await requests.rename_group(selected_level, group_name, gdi)
    await callback.answer(rename_group_reqeust)
    await manager.switch_to(FSM.Group.choose_group)
    # selected_level = manager.start_data['selected_level']

    # conn = await engine.connect_to_db()

    # try:
    #     group_number = await requests.find_or_create_group(conn, selected_level)
    #     await callback.answer(f"Группа {group_number} для уровня {selected_level} была создана.")
    # finally:
    #     await engine.close_db_connection(conn)

    

async def delete_group(callback: CallbackQuery, button: Button, manager: DialogManager):
    
    # conn = await engine.connect_to_db()
    eng_lvl_id = await requests.get_lvl_id(manager.start_data['selected_level'])
    group_id = manager.dialog_data.get('group_selected_id')
    group_details_id = await requests.get_group_details_id(eng_lvl_id, group_id)

    try:
        get_students = await db.fetch("""
            SELECT sd.id 
            FROM student_details sd
            WHERE sd.group_details_id = $1;
        """, group_details_id)
        
        students_id = [record['id'] for record in get_students]

        await db.execute("""
            UPDATE group_details 
            SET status = 'inactive' 
            WHERE id = $1
        """, group_details_id)

        if students_id:
            await db.execute("""
                UPDATE student_details 
                SET status = 'inactive' 
                WHERE id = ANY($1::int[])
            """, students_id)

        await callback.answer(f"✅ the group was successfully deleted!")
    except Exception as e:
        print(e)
        await callback.answer(f"❌ Group was not deleted. Please try again later.")
 
    await manager.switch_to(FSM.Group.choose_group)

    '''
    Это рабочий код на удаление группы вместе с учениками.

    conn = await engine.connect_to_db()
    eng_lvl_id = await requests.get_lvl_id(manager.start_data['selected_level'])
    group_id = manager.dialog_data.get('group_selected_id')
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
    '''


async def get_group_buttons(selected_level):
    groups = await requests.get_groups_for_level(selected_level)

    if groups:
        group_buttons = [
            (group_id['group_name'], Button(text=Const(f"Group: {group_id['group_name']}"), id=f"{group_id['id']}", on_click=group_selected))
            for group_id in groups
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
    await manager.update({"group_selected_name": await requests.get_group_number(int(item_id))})
    await manager.update({"group_selected_id": int(item_id)})
    #item_id это id группы, а не имя группы
        
    eng_lvl_id = await requests.get_lvl_id(manager.start_data['selected_level'])
    group_id = int(item_id)
    group_details_id = await requests.get_group_details_id(eng_lvl_id, group_id)
    
    student_names = await requests.get_students_from_group(group_details_id)
    all_students_group = [(name, id) for name, id in student_names]

    reminder = await get_reminder(all_students_group, group_details_id)
    if reminder:
        await callback.message.answer(f"‼️ 12 lessons have passed.\n⚠️ Have the students paid for the subscription?\n\n{reminder}")

    await manager.switch_to(FSM.Group.inside_group)


async def get_reminder(all_students_group, group_details_id): 
    students_to_notify = []

    for student_name, student_id in all_students_group:
        student_subs = await requests.get_attendance_remainder(await requests.get_student_details_id(student_id, group_details_id))
        # print(f"THIS IS REMAINDER: {student_subs['remainder']}")
        # print(f"THIS IS REM-OTHER: {student_subs['remainder'] - student_subs['other_days']}")
        if student_subs['remainder'] - student_subs['other_days'] == 0 and student_subs['total_classes'] > 0:
            students_to_notify.append(f"• {student_name}")
    
    if students_to_notify:
        students_list_to_notify = "\n".join(students_to_notify)
        return students_list_to_notify
    return None


async def editing_student(callback: CallbackQuery, button: Button, manager: DialogManager):
    eng_lvl_id = await requests.get_lvl_id(manager.start_data['selected_level'])
    group_id = manager.dialog_data.get('group_selected_id')
    
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
                                                         "group_selected_id": manager.dialog_data.get('group_selected_id'),
                                                         "group_selected_name": manager.dialog_data.get('group_selected_name'),
                                                         "student_buttons": student_buttons})

async def student_absence_selected(callback: CallbackQuery, button: Button, manager: DialogManager, item_id: str):
    print(f"This is student_absence_selected {int(item_id.split('_')[1])}") # здесь будет id_42 например
    await manager.update({"studentid_absence_selected": int(item_id.split('_')[1])})
    await manager.switch_to(FSM.Group.input_absence_reason)


async def add_student(callback: CallbackQuery, button: Button, manager: DialogManager):

    student_name = manager.find("student_name").get_value()
    group_details_id = await requests.get_group_details_id(
        await requests.get_lvl_id(manager.start_data['selected_level']),
        # await requests.get_group_number(int(manager.dialog_data.get('group_selected')))
        manager.dialog_data.get('group_selected_id')
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
    group_id = manager.dialog_data.get('group_selected_id')
    
    students = await requests.get_students_from_group(await requests.get_group_details_id(eng_lvl_id, group_id))
    student_names = [(name, id) for name, id in students]
 

    await manager.update({"show_group_students": student_names})
    await manager.switch_to(FSM.Group.student_group_view)


async def show_attendance(callback: CallbackQuery, button: Button, manager: DialogManager):
    await manager.start(FSM.Attendance.attendance, data={"selected_level": manager.start_data['selected_level'],
                                                         "group_selected_id": manager.dialog_data.get('group_selected_id'),
                                                         "group_selected_name": manager.dialog_data.get('group_selected_name')})
    
async def absence_reason(callback: CallbackQuery, button: Button, manager: DialogManager):
    current_date = datetime.now().date()

    absence = manager.find("absence_reason").get_value()
    
    try:
        group_details_id = await requests.get_group_details_id(
            await requests.get_lvl_id(manager.start_data['selected_level']),
            manager.dialog_data.get('group_selected_id')
            # await requests.get_group_number(int(manager.dialog_data.get('group_selected')))
        )
        student_details_id = await requests.get_student_details_id(manager.dialog_data.get('studentid_absence_selected'), group_details_id)

        await requests.add_student_absence_reason(student_details_id, current_date, absence)
        await callback.answer("✅ The data has been saved successfully!")
    except Exception as e:
        print(f"Error in absence_reason: {e}")
        await callback.answer("❌ An error occurred while saving the data. Please try again.")


async def absence_student_btns(callback: CallbackQuery, button: Button, manager: DialogManager):
    eng_lvl_id = await requests.get_lvl_id(manager.start_data['selected_level'])
    group_id = manager.dialog_data.get('group_selected_id')
    
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