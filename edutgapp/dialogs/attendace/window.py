import FSM

from aiogram_dialog.widgets.kbd import (
    Back, Button, Select, SwitchTo, 
    Group, Multiselect, Cancel
    )
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog import (
    Dialog, Window
)
from aiogram_dialog.widgets.input import TextInput
from dialogs.attendace.getters import get_data_attendance
from dialogs.attendace import handlers as action


async def attendance_window():
    # choose_year = SwitchTo(text=Const("⬅️ Back"), 
    #                 id="goto_year_btn", state=FSM.Attendance.attendance_year)
    choose_month = SwitchTo(text=Const("⬅️ Back"), id="goto_choose_btn", state=FSM.Attendance.attendance_month)
    # back_to_attendance_year =  SwitchTo(text=Const("⬅️ Back"), 
    #                     id="back_to_attendance_year", state=FSM.Attendance.attendance_month)
    back_to_custom_range =  SwitchTo(text=Const("⬅️ Back"), id="back_to_custom_range", state=FSM.Attendance.custom_range)
    
    dialog = Dialog(
        Window(
            Format("Select an option ⤵️"),
            Group(
                Button(Const("Excel"), id="attendance_excel", on_click=action.excel_alltime),
                Button(Const("Custom range"), id="custom_range", on_click=action.custom_range),  
                width=2,
            ),
            Cancel(text=Const("⬅️ Back")),
            state=FSM.Attendance.attendance,
        ),
        Window(
            Format("Select From and To dates;\nGet Excel button appears only when both are selected"),
            Group(
                Button(Const("Start Date"), id="year_start", on_click=action.choose_year_start),
                Button(Const("End Date"), id="year_end", on_click=action.choose_year_end),
                width=2,
            ),
            Button(Const("Get Excel"), id="get_custom_excel", on_click=action.excel_custom_range, when="extended"),
            Back(text=Const("⬅️ Back"), on_click=action.reset_data),
            state=FSM.Attendance.custom_range,
        ),
        Window(
            Format("Choose a year ⤵️"),
            Group(
                Select(
                    Format("{item.widget_id}"),
                    id="year",
                    item_id_getter=lambda x: x.widget_id,
                    items="get_years",
                    on_click=action.year_button_clicked,
                ),
                width=1,
            ),
            Cancel(text=Const("⬅️ Back")),
            state=FSM.Attendance.attendance_year,
        ),
        Window(
            Format("Choose a month ⤵️"),
            Select(
                Format("{item.widget_id}"),
                id="month",
                item_id_getter=lambda x: x.widget_id,
                items="get_months",
                on_click=action.month_button_clicked,
            ),
            SwitchTo(text=Const("⬅️ Back"), 
                        id="back_to_attendance_year", state=FSM.Attendance.attendance_year),
            state=FSM.Attendance.attendance_month,
        ),
        Window(
            Format("Choose a day ⤵️"),
            Group(
                Select(
                Format("{item.widget_id}"),
                id="day",
                item_id_getter=lambda x: x.widget_id,
                items="days_from",
                on_click=action.day_button_clicked,
                ),
                width=8,
            ),
            choose_month,
            state=FSM.Attendance.attendance_day_from,
        ),
        Window(
            Format("Choose a day ⤵️"),
            Group(
                Select(
                Format("{item.widget_id}"),
                id="day",
                item_id_getter=lambda x: x.widget_id,
                items="days_to",
                on_click=action.day_button_clicked,
                ),
                width=8,
            ),
            choose_month,
            state=FSM.Attendance.attendance_day_to,
        ),
        getter=get_data_attendance
    )

    return dialog


async def attendance_custom_range():
    dialog = Dialog(
        
    )

    return dialog