import os

from attendance import attendance_excel
from datetime import datetime
from aiogram.types import CallbackQuery, FSInputFile
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const
from aiogram_dialog import (
    DialogManager, ChatEvent, StartMode
)
from database import engine, requests
import FSM
from typing import Any


async def attendance_year_month_selecting(callback: CallbackQuery, button: Button, manager: DialogManager):
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

    await manager.switch_to(FSM.Attendance.attendance_year)


async def year_button_clicked(callback: CallbackQuery, button: Button, manager: DialogManager, item_id: str):
    
    await manager.update({"selected_year": item_id})
    await manager.switch_to(FSM.Attendance.attendance_month)


async def month_button_clicked(callback: CallbackQuery, button: Button, manager: DialogManager, item_id: str):
    
    eng_lvl_id = await requests.get_lvl_id(manager.start_data['selected_level'])
    group_id = await requests.get_group_number(int(manager.start_data['group_selected']))
    gdi = await requests.get_group_details_id(eng_lvl_id, group_id)

    month = await requests.get_num_by_month(requests.months_dict, item_id)
    year = manager.dialog_data.get('selected_year')
    eng_lvl = manager.start_data['selected_level']

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