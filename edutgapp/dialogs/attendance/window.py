import FSM

from database import requests
from aiogram_dialog.widgets.kbd import (
    Back, Button, Select, SwitchTo, 
    Group, Multiselect, Cancel
    )
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog import (
    Dialog, Window
)
from aiogram_dialog.widgets.input import TextInput
from dialogs.attendance.getters import get_data_attendance
from dialogs.attendance import handlers as action


async def attendance_window():
 
    dialog = Dialog(
        Window(
            Format("Select an option ⤵️"),
            Group(
                Button(Const("📋 All Times"), id="attendance_excel", on_click=action.excel_alltime),
                Button(Const("🎯 Custom Range"), id="custom_range", on_click=action.pass_starting_year),  
                width=2,
            ),
            Cancel(text=Const("⬅️ Back")),
            state=FSM.Attendance.attendance,
        ),
        Window(
            Format("Select the starting year ⤵️"),
            Group(
                Select(
                    Format("{item.widget_id}"),
                    id="year",
                    item_id_getter=lambda x: x.widget_id,
                    items="get_start_years",
                    on_click=action.starting_year_button_clicked,
                ),
                width=1,
            ),
            Back(text=Const("⬅️ Back")),
            state=FSM.Attendance.attendance_start_year,
        ),
        Window(
            Format("Select the starting month of {starting_year} ⤵️"),
            Select(
                Format("{item.widget_id}"),
                id="month",
                item_id_getter=lambda x: x.widget_id,
                items="get_start_months",
                on_click=action.starting_month_button_clicked,
            ),
            Back(text=Const("⬅️ Back")),
            state=FSM.Attendance.attendance_start_month,
        ),
        Window(
            Format("Select the starting day of {starting_month}.{starting_year} ⤵️"),
            Group(
                Select(
                Format("{item.widget_id}"),
                id="day",
                item_id_getter=lambda x: x.widget_id,
                items="get_starting_days",
                on_click=action.starting_day_button_clicked,
                ),
                width=8,
            ),
            Back(text=Const("⬅️ Back")),
            state=FSM.Attendance.attendance_start_day,
        ),
        Window(
            Format("Select the end year ⤵️"),
            Group(
                Select(
                    Format("{item.widget_id}"),
                    id="year",
                    item_id_getter=lambda x: x.widget_id,
                    items="get_end_years",
                    on_click=action.end_year_button_clicked,
                ),
                width=1,
            ),
            Back(text=Const("⬅️ Back")),
            state=FSM.Attendance.attendance_end_year,
        ),
        Window(
            Format("Select the end month of {end_year} ⤵️"),
            Select(
                Format("{item.widget_id}"),
                id="month",
                item_id_getter=lambda x: x.widget_id,
                items="get_end_months",
                on_click=action.end_month_button_clicked,
            ),
            Back(text=Const("⬅️ Back")),
            state=FSM.Attendance.attendance_end_month,
        ),
        Window(
            Format("Select the end day of {end_month}.{end_year} ⤵️"),
            Group(
                Select(
                Format("{item.widget_id}"),
                id="day",
                item_id_getter=lambda x: x.widget_id,
                items="get_end_days",
                on_click=action.end_day_button_clicked,
                ),
                width=8,
            ),
            Back(text=Const("⬅️ Back")),
            state=FSM.Attendance.attendance_end_day,
        ),
        Window(
            Format("{starting_day}.{starting_month}.{starting_year} — {end_day}.{end_month}.{end_year}"),
            Button(Const("Get Excel"), id="get_custom_excel", on_click=action.excel_custom_range),
            Back(text=Const("⬅️ Back")),
            state=FSM.Attendance.get_custom_excel,
        ),
        getter=get_data_attendance
    )

    return dialog