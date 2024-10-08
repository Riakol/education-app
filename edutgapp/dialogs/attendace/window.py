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
    dialog = Dialog(
        Window(
            Format("Select an option ⤵️"),
            Group(
                Button(Const("Excel"), id="attendance_excel", on_click=action.attendance_year_month_selecting), 
                width=2,
            ),
            Cancel(text=Const("⬅️ Back")),
            state=FSM.Attendance.attendance,
        ),
        Window(
            Format("Choose a year ⤵️"),
            Select(
                Format("{item.widget_id}"),
                id="year",
                item_id_getter=lambda x: x.widget_id,
                items="get_years",
                on_click=action.year_button_clicked,
            ),
            Cancel(text=Const("⬅️ Back")),
            state=FSM.Attendance.attendance_year,
        ),
        Window(
            Format("Choose a month of {selected_year} year ⤵️"),
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
        getter=get_data_attendance
    )

    return dialog