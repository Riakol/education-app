import os
import calendar

from typing import Dict
from datetime import datetime
from aiogram_dialog.widgets.common import Whenable
from attendance import attendance_excel
from aiogram.types import CallbackQuery, FSInputFile
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const
from aiogram_dialog import (
    DialogManager, ChatEvent, StartMode
)
from database import engine, requests
import FSM
from typing import Any


# async def year_button_clicked(callback: CallbackQuery, button: Button, manager: DialogManager, item_id: str):
    
#     eng_lvl_id = await requests.get_lvl_id(manager.start_data['selected_level'])
#     group_id = await requests.get_group_number(int(manager.start_data['group_selected']))
#     gdi = await requests.get_group_details_id(eng_lvl_id, group_id)

#     months = await requests.get_months_by_year(gdi, item_id)

#     get_months = [
#         Button(
#             text=Const(requests.months_dict[month]),
#             id=requests.months_dict[month],
#             on_click=month_button_clicked,
#         ) for month in months
#     ]

#     await manager.update({"get_months": get_months})


#     if not manager.dialog_data.get("year_start") and manager.dialog_data.get("year_end"):
#         await manager.update({"selected_year_to": item_id})
#         print(f"This is year To: {item_id}")
#     else:
#         await manager.update({"selected_year_from": item_id})
#         print(f"This is year From: {item_id}")      

#     await manager.switch_to(FSM.Attendance.attendance_month)

async def starting_year_button_clicked(callback: CallbackQuery, button: Button, manager: DialogManager, item_id: str):
    await manager.update({"starting_year": item_id})

    eng_lvl_id = await requests.get_lvl_id(manager.start_data['selected_level'])
    group_id = manager.start_data['group_selected_id']
    # group_id = await requests.get_group_number(int(manager.start_data['group_selected']))
    gdi = await requests.get_group_details_id(eng_lvl_id, group_id)

    months = await requests.get_months_by_year(gdi, item_id)

    get_months = [
        Button(
            text=Const(requests.months_dict[month]),
            id=requests.months_dict[month],
            on_click=starting_month_button_clicked,
        ) for month in months
    ]

    await manager.update({"get_start_months": get_months})

    await manager.switch_to(FSM.Attendance.attendance_start_month)

async def starting_month_button_clicked(callback: CallbackQuery, button: Button, manager: DialogManager, item_id: str):
    month = await requests.get_num_by_month(requests.months_dict, item_id)
    await manager.update({"starting_month": month})

    days = get_days_in_month(int(manager.dialog_data.get("starting_year")), month)        
    get_days = [
        Button(
            Const(str(day)),
            id=str(day),
            on_click=starting_day_button_clicked,
        ) for day in days
    ]
    await manager.update({"get_starting_days": get_days})
    await manager.switch_to(FSM.Attendance.attendance_start_day)


async def starting_day_button_clicked(callback: CallbackQuery, button: Button, manager: DialogManager, item_id: str):
    await manager.update({"starting_day": item_id})

    eng_lvl_id = await requests.get_lvl_id(manager.start_data['selected_level'])
    group_id = manager.start_data['group_selected_id']
    # group_id = await requests.get_group_number(int(manager.start_data['group_selected']))
    gdi = await requests.get_group_details_id(eng_lvl_id, group_id)
    
    month_year_data = await requests.get_month_year_from_attendace(gdi)
    years = set(month_year_data['year'])

    get_years = [
        Button(
            Const(str(year)),
            id=str(year),
            on_click=end_year_button_clicked,
        ) for year in years
    ]

    await manager.update({"get_end_years": get_years})
    await manager.switch_to(FSM.Attendance.attendance_end_year)


async def end_year_button_clicked(callback: CallbackQuery, button: Button, manager: DialogManager, item_id: str):
    await manager.update({"end_year": item_id})

    eng_lvl_id = await requests.get_lvl_id(manager.start_data['selected_level'])
    group_id = manager.start_data['group_selected_id']
    # group_id = await requests.get_group_number(int(manager.start_data['group_selected']))
    gdi = await requests.get_group_details_id(eng_lvl_id, group_id)

    months = await requests.get_months_by_year(gdi, item_id)

    get_months = [
        Button(
            text=Const(requests.months_dict[month]),
            id=requests.months_dict[month],
            on_click=starting_month_button_clicked,
        ) for month in months
    ]

    await manager.update({"get_end_months": get_months})

    await manager.switch_to(FSM.Attendance.attendance_end_month)


async def end_month_button_clicked(callback: CallbackQuery, button: Button, manager: DialogManager, item_id: str):
    month = await requests.get_num_by_month(requests.months_dict, item_id)
    await manager.update({"end_month": month})

    days = get_days_in_month(int(manager.dialog_data.get("end_year")), month)        
    get_days = [
        Button(
            Const(str(day)),
            id=str(day),
            on_click=starting_day_button_clicked,
        ) for day in days
    ]
    await manager.update({"get_end_days": get_days})
    await manager.switch_to(FSM.Attendance.attendance_end_day)


async def end_day_button_clicked(callback: CallbackQuery, button: Button, manager: DialogManager, item_id: str):
    await manager.update({"end_day": item_id})
    await manager.switch_to(FSM.Attendance.get_custom_excel)


# async def month_button_clicked(callback: CallbackQuery, button: Button, manager: DialogManager, item_id: str):
    
#     #item_id = September. name of the month not id
#     month = await requests.get_num_by_month(requests.months_dict, item_id)

#     if not manager.dialog_data.get("year_start") and manager.dialog_data.get("year_end"):
#         days_to = get_days_in_month(int(manager.dialog_data.get("selected_year_to")), month)
#         await manager.update({"selected_month_to": month})
#         get_days = [
#             Button(
#                 Const(str(day)),
#                 id=str(day),
#                 on_click=day_button_clicked,
#             ) for day in days_to
#         ]
#         await manager.update({"days_to": get_days})
#         await manager.switch_to(FSM.Attendance.attendance_day_to)
#     else:
#         days_from = get_days_in_month(int(manager.dialog_data.get("selected_year_from")), month)        
#         await manager.update({"selected_month_from": month})
#         get_days = [
#             Button(
#                 Const(str(day)),
#                 id=str(day),
#                 on_click=day_button_clicked,
#             ) for day in days_from
#         ]
#         await manager.update({"days_from": get_days})
#         await manager.switch_to(FSM.Attendance.attendance_day_from)


# async def day_button_clicked(callback: CallbackQuery, button: Button, manager: DialogManager, item_id: str):
#     print(f"This is day {item_id}")
#     if not manager.dialog_data.get("year_start") and manager.dialog_data.get("year_end"):
#         await manager.update({"selected_day_to": item_id})

#     else:
#         await manager.update({"selected_day_from": item_id})

#     await manager.switch_to(FSM.Attendance.custom_range)
    


async def excel_alltime(callback: CallbackQuery, button: Button, manager: DialogManager):
    
    eng_lvl_id = await requests.get_lvl_id(manager.start_data['selected_level'])
    group_id = manager.start_data['group_selected_id']
    group_name = manager.start_data['group_selected_name']
    gdi = await requests.get_group_details_id(eng_lvl_id, group_id)
    eng_lvl = manager.start_data['selected_level']

    data = await requests.attendance_alltime_data(gdi)
    transfer_data, student_name_dict = await get_student_transfer_info_from_group(gdi)
    
    file_path = await attendance_excel.create_attendance_excel(data, eng_lvl, group_name, transfer_data, student_name_dict)
    if os.path.exists(file_path):
        document = FSInputFile(file_path)
        await callback.answer('Sending a report...')
        await callback.bot.send_document(chat_id=callback.message.chat.id, document=document, caption=f"{eng_lvl}: {group_name}")

        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Error deleting file: {e}")


async def excel_custom_range(callback: CallbackQuery, button: Button, manager: DialogManager):
    start_date = datetime.strptime(f"{manager.dialog_data.get('starting_year')}-{manager.dialog_data.get('starting_month')}-{manager.dialog_data.get('starting_day')}", "%Y-%m-%d")
    end_date = datetime.strptime(f"{manager.dialog_data.get('end_year')}-{manager.dialog_data.get('end_month')}-{manager.dialog_data.get('end_day')}", "%Y-%m-%d")

    eng_lvl_id = await requests.get_lvl_id(manager.start_data['selected_level'])
    group_id = manager.start_data['group_selected_id']
    group_name = manager.start_data['group_selected_name']
    
    gdi = await requests.get_group_details_id(eng_lvl_id, group_id)

    eng_lvl = manager.start_data['selected_level']

    data = await requests.attendance_custom(gdi, start_date, end_date)
    transfer_data, student_name_dict = await get_student_transfer_info_from_group(gdi, start_date, end_date)


    
    file_path = await attendance_excel.create_attendance_excel(data, eng_lvl, group_name, transfer_data, student_name_dict, start_date=start_date, end_date=end_date)
    if os.path.exists(file_path):
        document = FSInputFile(file_path)
        await callback.answer('Sending a report...')
        await callback.bot.send_document(chat_id=callback.message.chat.id, document=document, caption=f"{eng_lvl}: {group_name}")

        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Error deleting file: {e}")
    
    await manager.done()


async def get_student_transfer_info_from_group(group_details_id, start_date=None, end_date=None):
    students_name_and_ids = await requests.get_students_from_group(group_details_id)
    students_ids = [student_id for _, student_id in students_name_and_ids]
    
    if start_date and end_date:
        transfer_data = await requests.get_transfer_info_custom(students_ids, start_date, end_date)
    else:
        transfer_data = await requests.get_transfer_info(students_ids)
    student_name_dict = {student_id: name for name, student_id in students_name_and_ids}
    
    return transfer_data, student_name_dict


async def pass_starting_year(callback: CallbackQuery, button: Button, manager: DialogManager):
    
    eng_lvl_id = await requests.get_lvl_id(manager.start_data['selected_level'])
    group_id = manager.start_data['group_selected_id']
    # group_id = await requests.get_group_number(int(manager.start_data['group_selected']))
    gdi = await requests.get_group_details_id(eng_lvl_id, group_id)
    
    month_year_data = await requests.get_month_year_from_attendace(gdi)
    years = set(month_year_data['year'])

    get_years = [
        Button(
            Const(str(year)),
            id=str(year),
            on_click=starting_year_button_clicked,
        ) for year in years
    ]


    await manager.update({"get_start_years": get_years})
    await manager.switch_to(FSM.Attendance.attendance_start_year)


def get_days_in_month(year, month):
    num_days = calendar.monthrange(year, month)[1]
    days = list(range(1, num_days + 1))
    return days
