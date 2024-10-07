import os
from datetime import datetime
from aiogram.types import CallbackQuery, FSInputFile
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const
from aiogram_dialog import (
    DialogManager, ChatEvent, 
)
from aiogram_dialog.widgets.kbd import ManagedCheckbox
from database import engine, requests
from FSM import StudentWorkflow
from typing import Any
from Attendance import attendance_excel, attendance_msg




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
    
    await manager.switch_to(StudentWorkflow.inside_group)


async def level_button_clicked(callback: CallbackQuery, button: Button, manager: DialogManager):
    selected_level = button.widget_id
    level_name = requests.levels[selected_level]
    manager.dialog_data['selected_level'] = level_name

    await manager.switch_to(StudentWorkflow.choose_group)

    # await manager.start(StudentWorkflow.choose_group)
    # manager.current_context().widget_data = manager.start_data
    
    # await manager.start(StudentWorkflow.choose_group, data={"selected_level": requests.levels[selected_level]})
    # manager.start_data
    #Да ладно, уже просто все нужные данные в widget data запихнул)
    # await manager.start(StudentWorkflow.choose_group, data=manager.current_context().widget_data)
    # await manager.start(StudentWorkflow.choose_group, data=manager.start_data('selected_level'))
    # await manager.start(StudentWorkflow.choose_group, data=manager.dialog_data)


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
    await manager.switch_to(StudentWorkflow.create_group)


async def create_group(callback: CallbackQuery, button: Button, manager: DialogManager):
    """ Обработка создания новой группы """
    selected_level = manager.dialog_data.get('selected_level')

    conn = await engine.connect_to_db()

    try:
        group_number = await requests.find_or_create_group(conn, selected_level)
        await callback.answer(f"Группа {group_number} для уровня {selected_level} была создана.")
    finally:
        await engine.close_db_connection(conn)

    await manager.switch_to(StudentWorkflow.choose_group)


async def delete_group_clicked(callback: CallbackQuery, button: Button, manager: DialogManager):
    await manager.switch_to(StudentWorkflow.delete_group)


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
 
    await manager.switch_to(StudentWorkflow.choose_group)


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
   
    await manager.switch_to(StudentWorkflow.select_group)


async def group_selected(callback: CallbackQuery, button: Button, manager: DialogManager, item_id: str):
    """ Действие при выборе группы """
    await manager.update({"group_selected": item_id})
    
    # await callback.answer(f"You selected {item_id}!")
    await manager.next()


async def add_student_to_group(callback: CallbackQuery, button: Button, manager: DialogManager):
  
    await manager.switch_to(StudentWorkflow.student_name)


async def remove_student_from_group(callback: CallbackQuery, button: Button, manager: DialogManager):
    print('x')
#     await manager.switch_to(StudentWorkflow.remove_student)
 
# async def remove_student(callback: CallbackQuery, button: Button, manager: DialogManager):
#     await manager.switch_to(StudentWorkflow.remove_student)

async def add_student(callback: CallbackQuery, button: Button, manager: DialogManager):

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
    await manager.switch_to(StudentWorkflow.student_group_view)


async def attendance_year_month_selecting(callback: CallbackQuery, button: Button, manager: DialogManager):
    eng_lvl_id = await requests.get_lvl_id(manager.dialog_data.get('selected_level'))
    group_id = await requests.get_group_number(int(manager.dialog_data.get('group_selected')))
    gdi = await requests.get_group_details_id(eng_lvl_id, group_id)
    
    month_year_data = await requests.get_month_year_from_attendace(gdi)
    years = set(month_year_data['year'])

    get_years = [
        Button(
            Const(str(year)),
            id=str(year),
            on_click=year_button_clicked,
        ) for year in years
    ]


    months = set(month_year_data['month'])

    get_months = [
        Button(
            text=Const(requests.months_dict[month]),
            id=requests.months_dict[month],
            on_click=month_button_clicked,
        ) for month in months
    ]

    await manager.update({"get_years": get_years})
    await manager.update({"get_months": get_months})

    await manager.switch_to(StudentWorkflow.attendance_year)

async def attendance(callback: CallbackQuery, button: Button, manager: DialogManager):
    await manager.switch_to(StudentWorkflow.attendance)


#Нужно решить как переиспользовать окно или диалог с получением года и месяца !
# async def get_attendance_msg(callback: CallbackQuery, button: Button, manager: DialogManager):
#     selected_month = button.widget_id
#     manager.dialog_data['selected_month'] = selected_month

#     eng_lvl_id = await requests.get_lvl_id(manager.dialog_data.get('selected_level'))
#     group_id = await requests.get_group_number(int(manager.dialog_data.get('group_selected')))
#     gdi = await requests.get_group_details_id(eng_lvl_id, group_id)

#     month = int(selected_month)
#     year = manager.dialog_data.get('selected_year')

#     data = await requests.attendance_data(gdi, month, year)
#     message = attendance_msg.create_attendance_report(data, month, year)
#     await callback.message.answer(message)


async def year_button_clicked(callback: CallbackQuery, button: Button, manager: DialogManager, item_id: str):
    
    await manager.update({"selected_year": item_id})
    await manager.switch_to(StudentWorkflow.attendance_month)

async def month_button_clicked(callback: CallbackQuery, button: Button, manager: DialogManager, item_id: str):
    
    eng_lvl_id = await requests.get_lvl_id(manager.dialog_data.get('selected_level'))
    group_id = await requests.get_group_number(int(manager.dialog_data.get('group_selected')))
    gdi = await requests.get_group_details_id(eng_lvl_id, group_id)

    month = await requests.get_num_by_month(requests.months_dict, item_id)
    year = manager.dialog_data.get('selected_year')
    eng_lvl = manager.dialog_data.get('selected_level')

    data = await requests.attendance_data(gdi, month, year)
   
    
    file_path = await attendance_excel.create_attendance_excel(data, month, year, eng_lvl, group_id)
    if os.path.exists(file_path):
        document = FSInputFile(file_path)
        await callback.answer('Sending a report...')
        await callback.bot.send_document(chat_id=callback.message.chat.id, document=document, caption=f"{eng_lvl}: {group_id}")

        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Error deleting file: {e}")

    # await manager.switch_to(StudentWorkflow.choose_group)  




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


