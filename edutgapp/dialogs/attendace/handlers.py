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


async def choose_year_start(callback: CallbackQuery, button: Button, manager: DialogManager):
    await manager.update({"year_start": button.widget_id})
    print(button.widget_id)
    await manager.switch_to(FSM.Attendance.attendance_year)
    
async def choose_year_end(callback: CallbackQuery, button: Button, manager: DialogManager):
    print(button.widget_id)
    await manager.update({"year_end": button.widget_id})
    await manager.switch_to(FSM.Attendance.attendance_year)

async def year_button_clicked(callback: CallbackQuery, button: Button, manager: DialogManager, item_id: str):
    
    eng_lvl_id = await requests.get_lvl_id(manager.start_data['selected_level'])
    group_id = await requests.get_group_number(int(manager.start_data['group_selected']))
    gdi = await requests.get_group_details_id(eng_lvl_id, group_id)

    months = await requests.get_months_by_year(gdi, item_id)

    get_months = [
        Button(
            text=Const(requests.months_dict[month]),
            id=requests.months_dict[month],
            on_click=month_button_clicked,
        ) for month in months
    ]

    await manager.update({"get_months": get_months})


    if not manager.dialog_data.get("year_start") and manager.dialog_data.get("year_end"):
        await manager.update({"selected_year_to": item_id})
        print(f"This is year To: {item_id}")
    else:
        await manager.update({"selected_year_from": item_id})
        print(f"This is year From: {item_id}")      

    await manager.switch_to(FSM.Attendance.attendance_month)



async def month_button_clicked(callback: CallbackQuery, button: Button, manager: DialogManager, item_id: str):
    
    #item_id = September. name of the month not id
    month = await requests.get_num_by_month(requests.months_dict, item_id)

    if not manager.dialog_data.get("year_start") and manager.dialog_data.get("year_end"):
        days_to = get_days_in_month(int(manager.dialog_data.get("selected_year_to")), month)
        await manager.update({"selected_month_to": month})
        get_days = [
            Button(
                Const(str(day)),
                id=str(day),
                on_click=day_button_clicked,
            ) for day in days_to
        ]
        await manager.update({"days_to": get_days})
        await manager.switch_to(FSM.Attendance.attendance_day_to)
    else:
        days_from = get_days_in_month(int(manager.dialog_data.get("selected_year_from")), month)        
        await manager.update({"selected_month_from": month})
        get_days = [
            Button(
                Const(str(day)),
                id=str(day),
                on_click=day_button_clicked,
            ) for day in days_from
        ]
        await manager.update({"days_from": get_days})
        await manager.switch_to(FSM.Attendance.attendance_day_from)


async def day_button_clicked(callback: CallbackQuery, button: Button, manager: DialogManager, item_id: str):
    print(f"This is day {item_id}")
    if not manager.dialog_data.get("year_start") and manager.dialog_data.get("year_end"):
        await manager.update({"selected_day_to": item_id})

    else:
        await manager.update({"selected_day_from": item_id})

    await manager.switch_to(FSM.Attendance.custom_range)
    


async def excel_alltime(callback: CallbackQuery, button: Button, manager: DialogManager):
    
    eng_lvl_id = await requests.get_lvl_id(manager.start_data['selected_level'])
    group_id = await requests.get_group_number(int(manager.start_data['group_selected']))
    gdi = await requests.get_group_details_id(eng_lvl_id, group_id)

    
    eng_lvl = manager.start_data['selected_level']

    data = await requests.attendance_alltime_data(gdi)
   
    
    file_path = await attendance_excel.create_attendance_excel(data, eng_lvl, group_id)
    if os.path.exists(file_path):
        document = FSInputFile(file_path)
        await callback.answer('Sending a report...')
        await callback.bot.send_document(chat_id=callback.message.chat.id, document=document, caption=f"{eng_lvl}: {group_id}")

        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Error deleting file: {e}")


async def excel_custom_range(callback: CallbackQuery, button: Button, manager: DialogManager):
    start_date = datetime.strptime(f"{manager.dialog_data.get('selected_year_from')}-{manager.dialog_data.get('selected_month_from')}-{manager.dialog_data.get('selected_day_from')}", "%Y-%m-%d")

    end_date = datetime.strptime(f"{manager.dialog_data.get('selected_year_to')}-{manager.dialog_data.get('selected_month_to')}-{manager.dialog_data.get('selected_day_to')}", "%Y-%m-%d")

    eng_lvl_id = await requests.get_lvl_id(manager.start_data['selected_level'])
    group_id = await requests.get_group_number(int(manager.start_data['group_selected']))
    gdi = await requests.get_group_details_id(eng_lvl_id, group_id)

    eng_lvl = manager.start_data['selected_level']

    data = await requests.attendance_custom(gdi, start_date, end_date)
   
  
    file_path = await attendance_excel.create_attendance_excel(data, eng_lvl, group_id)
    if os.path.exists(file_path):
        document = FSInputFile(file_path)
        await callback.answer('Sending a report...')
        await callback.bot.send_document(chat_id=callback.message.chat.id, document=document, caption=f"{eng_lvl}: {group_id}")

        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Error deleting file: {e}")
    
    await manager.done()


async def custom_range(callback: CallbackQuery, button: Button, manager: DialogManager):
    
    eng_lvl_id = await requests.get_lvl_id(manager.start_data['selected_level'])
    group_id = await requests.get_group_number(int(manager.start_data['group_selected']))
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

    await manager.update({"get_years": get_years})
    await manager.switch_to(FSM.Attendance.custom_range)


def get_days_in_month(year, month):
    num_days = calendar.monthrange(year, month)[1]
    days = list(range(1, num_days + 1))
    return days


async def reset_data(callback: CallbackQuery, button: Button, manager: DialogManager):
    await manager.update({
        "selected_year_from": None,
        "selected_month_from": None,
        "selected_year_to": None,
        "selected_month_to": None,
        "year_start": None,
        "year_end": None,
    })

    await manager.update({"extended": False})