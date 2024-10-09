import FSM

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
    all_students_group = [name for name, id in student_names]

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
    
    await manager.switch_to(FSM.Group.inside_group)


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


#DELETE
# async def delete_group_clicked(callback: CallbackQuery, button: Button, manager: DialogManager):
#     await manager.switch_to(FSM.Group.delete_group)


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
            # Button(text=Const(f"Group: {group_id['id']}"), id=f"{group_id['group_number']}", on_click=group_selected)
            # for group_id in groups
            (group_id['group_number'], Button(text=Const(f"Group: {group_id['id']}"), id=f"{group_id['group_number']}", on_click=group_selected))
            for group_id in groups
        ]
    else:
        group_buttons = [] 

    return group_buttons


async def get_groups_clicked(callback: CallbackQuery, button: Button, manager: DialogManager):
    """Обработчик для кнопки 'Select a group'."""
    
    # selected_level = await requests.get_lvl_id(manager.dialog_data.get('selected_level'))
    selected_level = await requests.get_lvl_id(manager.start_data["selected_level"])
    # user_id = callback.from_user.id
    # print(user_id)

    # await requests.insert_lvl_teacher_current_pos(selected_level, await requests.get_teacher_id(user_id))
    group_buttons = await get_group_buttons(selected_level)

    await manager.update({"selected_level": selected_level})
    await manager.update({"group_buttons": group_buttons})
   
    await manager.switch_to(FSM.Group.select_group)


async def group_selected(callback: CallbackQuery, button: Button, manager: DialogManager, item_id: str):
    """ Действие при выборе группы """
    await manager.update({"group_selected": item_id})
    
    # await callback.answer(f"You selected {item_id}!")
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
    else:
        student_buttons = []


    await manager.start(FSM.Student.editing_student_menu, data={"selected_level": manager.start_data['selected_level'],
                                                         "group_selected": manager.dialog_data.get('group_selected'),
                                                         "student_buttons": student_buttons})


async def add_student(callback: CallbackQuery, button: Button, manager: DialogManager):

    student_name = manager.find("student_name").get_value()
    if student_name:
        await requests.add_student(student_name)
        student_id = await requests.get_student_id(student_name)
        eng_lvl_id = await requests.get_lvl_id(manager.start_data['selected_level'])
        group_id = await requests.get_group_number(int(manager.dialog_data.get('group_selected')))

        await requests.add_student_to_group(student_id, await requests.get_group_details_id(eng_lvl_id, group_id))

    
    # await manager.next()
    

async def show_students(callback: CallbackQuery, button: Button, manager: DialogManager):
    eng_lvl_id = await requests.get_lvl_id(manager.start_data['selected_level'])
    group_id = await requests.get_group_number(int(manager.dialog_data.get('group_selected')))
    
    students = await requests.get_students_from_group(await requests.get_group_details_id(eng_lvl_id, group_id))
    student_names = [name for name, id in students]
 

    await manager.update({"show_group_students": student_names})
    await manager.switch_to(FSM.Group.student_group_view)


async def show_attendance(callback: CallbackQuery, button: Button, manager: DialogManager):
    await manager.start(FSM.Attendance.attendance, data={"selected_level": manager.start_data['selected_level'],
                                                         "group_selected": manager.dialog_data.get('group_selected')})


async def dialog_get_data(dialog_manager: DialogManager, **kwargs):
    context = dialog_manager.current_context()
    data = context.dialog_data

    return {
        "group_buttons": data.get("group_buttons", []), 
        "name": "Obayash", 
        "selected_level": data.get("selected_level"),
        "group_selected": data.get("group_selected"),     
        "students_view": data.get("show_group_students"),

        "get_years": data.get("get_years"),
        "get_months": data.get("get_months"),
        "selected_year": data.get("selected_year"),
        "selected_month": data.get("selected_month"),
             
    }


